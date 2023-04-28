from nonebot.exception import MatcherException
from nonebot.params import CommandArg,Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot import on_command,logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent,helpers,MessageSegment,Message,GroupMessageEvent
from .utils import MangaTranslator 

__plugin_meta__ = PluginMetadata(
    name="图片翻译",
    description="利用api翻译图片并返回翻译后的图片",
    usage="""指令：
        图片翻译 [图片] --翻译并返回翻译后的图片
        多图片翻译 [图片]*n --翻译并返回多张翻译后的图片
""",
)

pictrans= on_command("图片翻译", priority=5, block=False,aliases={"翻译图片"})
mul_pictrans=on_command("多图片翻译",priority=5,block=False)
manga_trans=MangaTranslator()


@pictrans.handle()
async def _(event:MessageEvent,matcher:Matcher,args:Message=CommandArg()):
    if event.reply:
        args=event.reply.message
    if img_list:=helpers.extract_image_urls(args):
        matcher.set_arg("img_list",img_list)
   

@pictrans.got("img_list", prompt="请发送要翻译的图片")
async def handle_event(event: MessageEvent,img_list:list=Arg()):
        try:
            img_url_list = helpers.extract_image_urls(event.message)
            if not img_url_list:
                img_url_list=img_list
            result = await manga_trans.call_api(img_url_list[0])
            await pictrans.send(message=f"翻译完成,当前api:{result[1]}")
            await pictrans.finish(message=MessageSegment.image(result[0]))
        except MatcherException:
            raise
        except Exception as e:
            logger.warning(f"翻译失败:{e}")
            await pictrans.send("翻译失败,错误信息见控制台输出")



@mul_pictrans.handle()
async def _(event:MessageEvent,matcher:Matcher,args:Message=CommandArg()):
    if img_list:=helpers.extract_image_urls(args):
        matcher.set_arg("img_list",img_list)
        
@mul_pictrans.got("img_list",prompt="请发送要翻译的图片，发送/退出以退出多图片模式")
async def _(bot:Bot,event:MessageEvent,img_list:list=Arg()):
    id=event.group_id if isinstance(event,GroupMessageEvent) else event.user_id
    if new_list:=helpers.extract_image_urls(event.message):
        manga_trans.img_url.extend(new_list)
        await mul_pictrans.reject("请继续发送图片，若想退出请发送/退出")
    else:
        await mul_pictrans.send("图片接收完毕，处理中")
    forward_msg=[]
    for i,url in enumerate(manga_trans.img_url):
        pic=await manga_trans.call_api(url)
        forward_msg.append({"type":"node","data":{"name":"翻译姬","uin":str(bot.self_id),"content":"P"+str(i)+",API:"+pic[1]+"\n"+MessageSegment.image(pic[0])}})
    await bot.send_group_forward_msg(group_id=id,messages=forward_msg) if isinstance(event,GroupMessageEvent) else await bot.send_private_forward_msg(user_id=id,messages=forward_msg)
    manga_trans.img_url.clear()
    
    

from nonebot.exception import MatcherException
from nonebot.params import CommandArg, Arg, ArgPlainText
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot import on_command, logger, get_plugin_config, require
from nonebot.adapters import Message, Event, Bot
from datetime import datetime
from typing import List

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import CustomNode, Image, Reference, UniMessage
from nonebot_plugin_alconna.uniseg.tools import image_fetch, reply_fetch
from nonebot_plugin_alconna.uniseg import UniMsg, Reply
from .utils import MangaTranslator, BytesIO
from .config import Config


__plugin_meta__ = PluginMetadata(
    name="图片翻译",
    description="利用api翻译图片并返回翻译后的图片",
    usage="""指令：
        图片翻译 [图片] --翻译并返回翻译后的图片
        多图片翻译 [图片]*n --翻译并返回多张翻译后的图片
        切换翻译api [api] --将该api的优先级设为最高
""",
    type="application",
    homepage="https://github.com/maoxig/nonebot-plugin-manga-translator",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

pictrans = on_command("图片翻译", priority=5, block=False, aliases={"翻译图片"})
mul_pictrans = on_command("多图片翻译", priority=5, block=False)
api_change = on_command(
    "翻译api切换", priority=5, aliases={"翻译API切换", "切换翻译api", "切换翻译API"}
)


MangaTrans_Config = get_plugin_config(Config)

manga_trans = MangaTranslator(MangaTrans_Config)


@api_change.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("text", args)


@api_change.got(
    "text",
    prompt="请输入api名称，可用api有" + str([api.__name__ for api in manga_trans.api]),
)
async def _(text: str = ArgPlainText()):
    if text not in [api.__name__ for api in manga_trans.api]:
        await api_change.finish("无效名称，请检查输入")
    else:
        api_dict = {api.__name__: api for api in manga_trans.api}
        api = api_dict[text]
        manga_trans.api.insert(0, manga_trans.api.pop(manga_trans.api.index(api)))
        await api_change.finish(f"{text}的优先级已设为最高")


@pictrans.handle()
async def _(
    bot: Bot,
    msg: UniMsg,
    event: Event,
    state: T_State,
    matcher: Matcher,
):
    if msg.has(Reply):
        if (reply := await reply_fetch(event, bot)) and reply.msg:
            reply_msg = reply.msg
            uni_msg_with_reply = UniMessage.generate_without_reply(message=reply_msg)
        msg.extend(uni_msg_with_reply)

    if img_list := await extract_images(bot=bot, event=event, state=state, msg=msg):
        matcher.set_arg("img_list", img_list)


@pictrans.got("img_list", prompt="请发送要翻译的图片")
async def handle_event(
    bot: Bot,
    msg: UniMsg,
    event: Event,
    state: T_State,
    img_list: list = Arg(),
):
    try:
        img_url_list = await extract_images(bot=bot, event=event, state=state, msg=msg)
        if not img_url_list:
            img_url_list = img_list
        result = await manga_trans.call_api(img_url_list[0])
        await pictrans.send(message=f"翻译完成,当前api:{result[1]}")
        await UniMessage.image(raw=result[0]).send()
    except MatcherException:
        raise
    except Exception as e:
        logger.warning(f"翻译失败:{e}")
        await pictrans.send("翻译失败,错误信息见控制台输出")


@mul_pictrans.handle()
async def _(
    bot: Bot,
    msg: UniMsg,
    event: Event,
    state: T_State,
    matcher: Matcher,
):
    if img_list := await extract_images(bot=bot, event=event, state=state, msg=msg):
        matcher.set_arg("img_list", img_list)


@mul_pictrans.got("img_list", prompt="请发送要翻译的图片，发送/退出以退出多图片模式")
async def _(
    bot: Bot, msg: UniMsg, event: Event, state: T_State, img_list: list = Arg()
):

    if new_list := await extract_images(bot=bot, event=event, state=state, msg=msg):
        manga_trans.img_url.extend(new_list)
        await mul_pictrans.reject("请继续发送图片，若想退出请发送/退出")
    else:
        await mul_pictrans.send("图片接收完毕，处理中")
    imgs = []
    for img_url in manga_trans.img_url:
        result = await manga_trans.call_api(img_url)
        imgs.append(result[0])

    try:
        await send_forward_msg(bot, event, imgs)
    except Exception as e:
        logger.warning("无法发送合并消息")
        for img in imgs:
            await UniMessage.image(raw=img).send()
    manga_trans.img_url.clear()


async def extract_images(
    bot: Bot, event: Event, state: T_State, msg: UniMsg
) -> List[BytesIO]:
    imgs = []
    for msg_seg in msg:
        if isinstance(msg_seg, Image):
            imgs.append(
                await image_fetch(bot=bot, event=event, state=state, img=msg_seg)
            )

    return imgs


async def send_forward_msg(
    bot: Bot,
    event: Event,
    images: List[BytesIO],
):
    try:
        from nonebot.adapters.onebot.v11 import Bot as V11Bot
        from nonebot.adapters.onebot.v11 import Event as V11Event
        from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
        from nonebot.adapters.onebot.v11 import Message as V11Msg
        from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg

        async def send_forward_msg_v11(
            bot: V11Bot,
            event: V11Event,
            name: str,
            uin: str,
            msgs: List[V11Msg],
        ):
            messages = [
                {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}
                for msg in msgs
            ]
            if isinstance(event, V11GMEvent):
                await bot.call_api(
                    "send_group_forward_msg", group_id=event.group_id, messages=messages
                )
            else:
                await bot.call_api(
                    "send_private_forward_msg",
                    user_id=event.get_user_id(),
                    messages=messages,
                )

        if isinstance(bot, V11Bot) and isinstance(event, V11Event):
            await send_forward_msg_v11(
                bot,
                event,
                "翻译姬",
                bot.self_id,
                [V11Msg(V11MsgSeg.image(img)) for img in images],
            )
            return

    except ImportError:
        pass

    uid = bot.self_id
    name = "翻译姬"
    time = datetime.now()
    await UniMessage(
        Reference(
            content=[
                CustomNode(uid, name, time, await UniMessage.image(raw=img).export())
                for img in images
            ]
        )
    ).send()

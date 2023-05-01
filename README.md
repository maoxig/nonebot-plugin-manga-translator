<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot-plugin-manga-translator

✨*基于Nonebot2的图片/漫画翻译插件*✨
  
<div align="left">
  
## 💿安装
通过`pip`或`nb`安装；

- 使用nb:
  在机器人目录下命令行使用
  `nb plugin install nonebot_plugin_manga_translator`
- 使用pip(不推荐):
  ~~不推荐就是不推荐，略略略~~

## 📖简介

1. 适配多种api,将收到的图片翻译并发送翻译后的图片，支持批量操作

2. ⚙️插件配置

这些配置项必填，否则无法使用，请在机器人目录下的.env.*里填写以下选项(至少填一个平台的)

~~个人感觉有道API的效果比百度好很多，但是架不住百度每个月前1w次调用免费啊~~

|       配置项        | 类型  | 默认值 |          示例           | 说明    |
| :-----------------: | :---: | :-----: | :------------------------: | :------- |
|     有道翻译API     |   -   |    -    |             -              | -        |
|   youdao_app_key    |  str  |   ""    |   youdao_app_key="xxxxx"   | 应用ID   |
|  youdao_app_secret  |  str  |   ""    | youdao_app_secret="xxxxxx" | 应用秘钥 |
|     百度翻译API     |   -   |    -    |             -              | -        |
|    baidu_app_id     |  str  |   ""    |    baidu_app_id="66666"    | APP ID   |
|    baidu_app_key    |  str  |   ""    |   baidu_app_key="xxxxxx"   | 密钥     |
|     离线翻译API     |   -   |    -    |             -              | -        |
|    offline_url    |  str  |   ""    |   offline_url="http://127.0.0.1:5003"   | 见下方说明     |
| 其他翻译API(待更新) |   -   |    -    |             -              | -        |

## 🌙更新日志

</details>
</summary>点击展开</summary>

- 2023-05-01:

  - 添加切换api的功能，你可以将某个api优先级设为最高
  - 适配离线翻译api[manga-image-translator](https://github.com/zyddnys/manga-image-translator),现在你可以体验本地的翻译

- 2023-04-28:

  插件发布

</details>

## 🎉命令

1. 图片翻译 [图片]：单张图片翻译，也可以先发送/图片翻译再发送图片,可以如下组合

    1. 文字+图片
    2. 先文字，后图片
    3. 文字回复图片

2. 多图片翻译 [图片]：n张图片翻译，将会以合并转发消息的形式发出,可以如下组合

    1. 先文字，后多张图片 
    2. 2.文字+图片*n
3. 切换翻译api [api]: 将该api优先级提到最高，目前有`youdao baidu offline`

未完待续

## ⭐效果图

<img src="https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图1.jpg" width="180" height="180">
<img src="https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图2.jpg" width="180" height="180">
<img src="https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图3.jpg" width="180" height="180">
<img src="https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图4.png" width="180" height="180">

## 🔑API获取

</details>
</summary>有道翻译</summary>

1. 在[有道智云AI开放平台](https://ai.youdao.com/#/)注册并登录后，进入控制台
2. 在左侧`自然语言翻译服务`里的`图片翻译`里创建应用，选择服务和接入方式分别为`图片翻译`和`API`，其他项随意。
![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/有道翻译.png)
3. 创建后将`应用ID`和`应用秘钥`按照上面的配置说明分别填入.env.*文件里即可

</details>

</details>
</summary>百度翻译</summary>

   1. 在[百度翻译开放平台](https://api.fanyi.baidu.com/)注册并登录
   2. 找到`产品服务`的`图片翻译`,申请创建
   3. 创建后在`管理控制台`的`总览`中找到`APP ID`和`密钥`,根据上面的配置说明填入.env.*文件

</details>

</details>
</summary>离线翻译</summary>
(该方案对设备配置要求较高，建议在有足够的硬盘空间、内存、显存，或有一台能为bot处理请求的服务器时考虑使用该方案)

   1. 参考[manga-image-translator](https://github.com/zyddnys/manga-image-translator)的说明，克隆仓库，并安装相关依赖(可能需要额外安装`pydensecrf`)
   2. 安装好依赖后，在仓库目录下运行

      ```python
      python -m manga_translator -v --mode web --use-cuda# the demo will be serving on http://127.0.0.1:5003
      ```

   3. 如果你的设备没有成功安装cuda(要求pytorch的版本和cuda对应，不对应请重装)，请去掉参数`--use-cuda`，如果图片处理过程中爆显存，请改成`--use-cuda-limited`

   4. 你可以访问控制台给出的网址，尝试先本地翻译一张图片，此时会根据选项下载需要的模型(为防止下载失败，也可以提前手动下载)
   5. 如果bot和翻译器在同一台设备，那么.env填写`offline_url="http://127.0.0.1:5003"`即可，如果不在同一台设备，你**可能**还需要放行防火墙、端口转发等，并且填写内容也会有所变化
   6. 最后你**可能**还需要修改一下本插件的代码，找到本插件`utils.py`的`offline`函数，根据注释和[文档](https://github.com/zyddnys/manga-image-translator/blob/main/README.md),修改字典`data`，从而指定你想要的OCR模型和翻译模型(目前是用了offline模型,你可以改成别的)

</details>

## 🐦计划

- [x] 支持部署离线翻译模型

- [ ] 支持更多API

- [ ] 完善插件

## 喜欢的话就点个star✨吧QAQ

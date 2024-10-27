<!-- markdownlint-disable MD033 -->
<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot-plugin-manga-translator

✨*基于Nonebot2的图片/漫画翻译插件*✨

<a href="https://github.com/nonebot/nonebot2">
  <img src="https://img.shields.io/badge/nonebot-v2-red" alt="nonebot">
</a>
<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/maoxig/nonebot-plugin-manga-translator" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-manga-translator">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-manga-translator" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

<div align="left">

## 💿安装

通过`pip`或`nb`安装；

- 使用nb:
  在机器人目录下命令行使用
  `nb plugin install nonebot_plugin_manga_translator`
- 使用pip(不推荐):
  `pip install nonebot_plugin_manga_translator`
  之后在机器人`pyproject.toml`里的`plugins = []`列表追加`"nonebot_plugin_manga_translator"`

## 📖简介

1. 适配多种api,将收到的图片翻译并发送翻译后的图片，支持批量操作

2. 本插件0.2.0版本开始基于[nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna/tree/master)插件，适配了多平台（不一定稳定，欢迎提issue或pr），之前的版本(<=0.1.3)支持onebot.v11适配器

## ⚙️插件配置

### 配置驱动器​

为了适配多平台，从0.2.0以及之后的版本插件需要“客户端型驱动器”（如 httpx）来下载图片等，驱动器安装和配置参考 [NoneBot 选择驱动器](https://nonebot.dev/docs/advanced/driver)

~~我知道很少人会去看，所以你可以直接按照下面两步操作~~

首先找到你的平台协议需要的驱动器，大部分情况下可以httpx，例如

```
nb driver install httpx
```

并且需要在 `.env.*` 配置文件中启用对应的驱动器，例如：

```
DRIVER=~fastapi+~httpx
```

### 获取API

请在机器人目录下的.env.*里填写以下选项(至少填一个平台的，如果没有就不用填)，获取方式已整理好，见下方

~~个人感觉就漫画翻译而言,这几家API的效果大致为有道>=百度≈离线>=火山,且火山翻译对竖版日文的翻译效果很差，不过离线API可以通过修改模型来获得自定义的效果~~

|          配置项           | 类型  |                   默认值                    |                           示例                           | 说明                                                                                   | API定价                                                    |
| :-----------------------: | :---: | :-----------------------------------------: | :------------------------------------------------------: | :------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
|        有道翻译API        |   -   |                      -                      |                            -                             | -                                                                                      | 新用户送一定额度,梯度收费，0<月调用量<100w时,0.04元/张     |
|      youdao_app_key       |  str  |                     ""                      |                  youdao_app_key="xxxxx"                  | 应用ID                                                                                 |                                                            |
|     youdao_app_secret     |  str  |                     ""                      |                youdao_app_secret="xxxxxx"                | 应用秘钥                                                                               |                                                            |
|        百度翻译API        |   -   |                      -                      |                            -                             | -                                                                                      | 每月1万次免费调用量，之后按梯度收费,最高0.04元/次          |
|       baidu_app_id        |  str  |                     ""                      |                   baidu_app_id="66666"                   | APP ID                                                                                 |                                                            |
|       baidu_app_key       |  str  |                     ""                      |                  baidu_app_key="xxxxxx"                  | 密钥                                                                                   |                                                            |
|        火山翻译API        |   -   |                      -                      |                            -                             | -                                                                                      | 每月前100张免费，之后0.04元/张                             |
|   huoshan_access_key_id   |  str  |                     ""                      |              huoshan_access_key_id="AK***"               | Access Key ID                                                                          |                                                            |
| huoshan_secret_access_key |  str  |                     ""                      |             huoshan_secret_access_key="UT**"             | Secret Access Key                                                                      |                                                            |
|        离线翻译API        |   -   |                      -                      |                            -                             | -                                                                                      | 可能是电费?                                                |
|        offline_url        |  str  |                     ""                      |          offline_url="<http://127.0.0.1:5003>"           | 见下方说明                                                                             |                                                            |
|       offline_api_data        | dict  | {"translator": "youdao", "tgt_lang": "CHS"} | offline_api_data={"translator": "youdao", "tgt_lang": "CHS"} | 参考 [manga-image-translator](https://github.com/zyddnys/manga-image-translator)的文档 | 需要注意.env里面填写如果字典是跨行字典，需要添加一层单引号包裹 |
|    其他翻译API(待更新)    |   -   |                      -                      |                            -                             | -                                                                                      |                                                            |

## 🔑API获取

<details>
<summary>有道翻译</summary>

1. 在[有道智云AI开放平台](https://ai.youdao.com/#/)注册并登录后，进入控制台
2. 在左侧`自然语言翻译服务`里的`图片翻译`里创建应用，选择服务和接入方式分别为`图片翻译`和`API`，其他项随意。
![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/有道翻译.png)
3. 创建后将`应用ID`和`应用秘钥`按照上面的配置说明分别填入.env.*文件里即可

</details>

<details>
<summary>百度翻译</summary>

   1. 在[百度翻译开放平台](https://api.fanyi.baidu.com/)注册并登录
   2. 找到`产品服务`的`图片翻译`,申请创建
   3. 创建后在`管理控制台`的`总览`中找到`APP ID`和`密钥`,根据上面的配置说明填入.env.*文件

</details>

<details>
<summary>火山翻译</summary>

   1. 根据火山引擎的[文档](https://www.volcengine.com/docs/4640/130872)，按流程注册
   2. 创建好服务后获取到密钥，分别为`Access Key ID`和`Secret Access Key`，然后点击`Secret Access Key`下的按钮显示出密钥
   3. 分别根据上面的配置说明填入.env.*文件

</details>

<details>
<summary>离线翻译</summary>
(该方案对设备配置要求较高，建议在有足够的硬盘空间、内存、显存，或有一台能为bot处理请求的服务器时考虑使用该方案)

   1. 参考[manga-image-translator](https://github.com/zyddnys/manga-image-translator)的说明，克隆仓库，并安装相关依赖(可能需要额外安装`pydensecrf`)
   2. 安装好依赖后，在仓库目录下运行

      ```python
      python -m manga_translator -v --mode web --use-cuda
      # the demo will be serving on http://127.0.0.1:5003，此时会提供一个网页，可以点击打开
      ```

   3. 如果你的设备没有成功安装cuda(要求pytorch的版本和cuda对应，不对应请重装)，请去掉参数`--use-cuda`，如果图片处理过程中爆显存，请改成`--use-cuda-limited`

   4. 你可以访问控制台给出的网址，**尝试先手动翻译一张图片**，此时会根据选项下载需要的模型(为防止下载失败，也可以提前手动下载)
   5. 如果bot和翻译器在同一台设备，那么.env填写`offline_url="http://127.0.0.1:5003"`即可，如果不在同一台设备，你**可能**还需要放行防火墙、端口转发等，并且填写内容也会有所变化
   6. 关于.env填写的offline_api_data，需要参考[文档](https://github.com/zyddnys/manga-image-translator/blob/main/README.md),修改字典`data`，从而指定你想要的OCR模型和翻译模型以及修复模型。需要注意在填写.env时，如果是多行字典，参考[NB文档](https://nonebot.dev/docs/next/appendices/config#%E9%85%8D%E7%BD%AE%E9%A1%B9%E8%A7%A3%E6%9E%90)，需要在外面添加引号，例如
    
      ```
      offline_api_data =
      '
      {
        "translator": "youdao",
        "tgt_lang": "CHS",
        "ocr": "mocr"
      }
      '
      ```

      单行字典则不需要
      ```
      offline_api_data ={"translator": "youdao","tgt_lang": "CHS","ocr": "mocr"}
      ```
</details>

## 🎉命令

1. 图片翻译 [图片]：单张图片翻译，也可以先发送/图片翻译再发送图片,可以如下组合

    1. 文字+图片
    2. 先文字，后图片
    3. 文字回复图片

2. 多图片翻译 [图片]：n张图片翻译，将会以合并转发消息（如果平台支持，否则则一张一张发出）的形式发出,可以如下组合

    1. 先文字，后多张图片
    2. 文字+图片*n
3. 切换翻译api [api]: 将该api优先级提到最高，目前有`youdao baidu huoshan offline`

未完待续

## ⭐效果图

![效果图1](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图1.jpg)
![效果图2](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图2.jpg)
![效果图3](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图3.jpg)
![效果图4](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图4.PNG)

## 🌙更新日志

<details>
<summary>点击展开</summary>

- 2024-10-27:

  - 将offline的配置移到.env，增强错误提示

- 2024-08-17:

  - 兼容pydantic V2

- 2024-04-23:

  - 更新PIL版本，修复压缩png图片时失败

- 2024-04-23:

  - 更新版本，这个版本起开始基于[nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna/tree/master)插件支持多适配器多平台(可能有bug)，同时更新nonebot2依赖至2.2.0以上

- 2023-06-09:

  - 更新插件元数据

- 2023-05-03:

  - 更新说明文档
  - 适配[火山翻译api](https://translate.volcengine.com/api),你可以选择接入火山翻译提供的API

- 2023-05-01:

  - 添加切换api的功能，你可以将某个api优先级设为最高
  - 适配离线翻译api[manga-image-translator](https://github.com/zyddnys/manga-image-translator),现在你可以体验本地的翻译

- 2023-04-28:

  - 插件发布

</details>

## 🐦计划

- [x] 适配离线翻译模型[manga-image-translator](https://github.com/zyddnys/manga-image-translator)

- [x] 支持更多API

- [x] 多平台适配

- [ ] 优化代码

- [ ] 支持指定源语言和目标语言

- [ ] 完善插件

## ✨喜欢的话就点个star✨吧，球球了QAQ

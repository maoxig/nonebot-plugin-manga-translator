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
  ~~既然不推荐就不要想着这样安装了啊喂~~

## 📖简介

1. 适配多种api,将收到的图片翻译并发送翻译后的图片，支持批量操作

2. ⚙️插件配置

这些配置项必填，否则无法使用，请在机器人目录下的.env.*里填写以下选项(不同平台API填一份就行)

~~个人感觉有道API的效果比百度好很多，但是架不住百度每个月前1w次调用免费啊~~

|       config        | type  | default |          example           | usage    |
| :-----------------: | :---: | :-----: | :------------------------: | :------- |
|     有道翻译API     |   -   |    -    |             -              | -        |
|   youdao_app_key    |  str  |   ""    |   youdao_app_key="xxxxx"   | 应用ID   |
|  youdao_app_secret  |  str  |   ""    | youdao_app_secret="xxxxxx" | 应用秘钥 |
|     百度翻译API     |   -   |    -    |             -              | -        |
|    baidu_app_id     |  str  |   ""    |    baidu_app_id="11451"    | APP ID   |
|    baidu_app_key    |  str  |   ""    |   baidu_app_key="xxxxxx"   | 密钥     |
| 其他翻译API(待更新) |   -   |    -    |             -              | -        |

## 🌙更新日志

<details>
<summary>点击展开</summary>

- 2023-04-28:

  插件发布

</details>

## 🎉命令

1. 图片翻译 图片：单张图片翻译，也可以先发送/图片翻译再发送图片

    支持 1.文字+图片 2.先文字，后图片 3.文字回复图片

2. 多图片翻译 图片：如 图片翻译 图片*n ; n张图片翻译，将会以合并转发消息的形式发出

    支持 1. 先文字，后多张图片 2. 文字+图片*n

未完待续

## ⭐效果图

![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图1.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图2.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/效果图3.jpg)

## 🔑API-key获取

<details>
<summary>有道翻译</summary>

1. 在[有道智云AI开放平台](https://ai.youdao.com/#/)注册并登录后，进入控制台
2. 在左侧`自然语言翻译服务`里的`图片翻译`里创建应用，选择服务和接入方式分别为`图片翻译`和`API`，其他项随意。
![Image text](https://github.com/maoxig/nonebot-plugin-manga-translator/blob/main/resource/有道翻译.png)
3. 创建后将`应用ID`和`应用秘钥`按照上面的配置说明分别填入.env文件里即可

</details>

<details>
<summary>百度翻译</summary>

   1. 在[百度翻译开放平台](https://api.fanyi.baidu.com/)注册并登录
   2. 找到`产品服务`的`图片翻译`,申请创建
   3. 创建后在`管理控制台`的`总览`中找到`APP ID`和`密钥`,根据上面的配置说明填入.env文件

</details>

## 🐦计划

- [ ] 支持更多API

- [ ] 支持部署离线翻译模型

- [ ] 完善插件

## 喜欢的话就点个star✨吧QAQ

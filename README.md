# Hinata

See [Docs](https://v2.nonebot.dev/)

一只可爱(且色情?)的QQ群聊bot



声明一下:
本仓库储存的是本人的私人bot
代码大多来自nonebot社区   (°ー°〃)


要是真的有路人看到的话就按照一下方式搭建
下面的方式搭建你不会学习到任何知识,我的建议是 (https://v2.nonebot.dev/) 从零开始学习搭建以及使用社区的插件再到自己写插件




以下为纯萌新搭建此bot教程:
测试环境为虚拟机上新安装的windows10 21h2
1. 安装python3,记得勾选Add to path(我自己用的是python 3.10.4)
2. Windows强烈建议安装好 C++ Build Tools 以及 Microsoft Visual C++ 2013 Redistributable Package
3. 双击 "换源安装一些依赖.bat" 安装一些必要的环境
4. 使用控制台cd到hinata文件夹目录(bot.py的那个),输入nb run或python bot.py运行bot
5. 进入go-cqhttp文件夹
6. 双击 "go-cqhttp.bat" 扫码并且登陆,账号登陆缓存为go-cqhttp文件夹下的session.token,需要换号登陆删除即可
7. 登陆失败就多试几次,本地端登不上就连接同一局域网登陆. 服务器端登不上就本地先登,登上了把gocqhttp复制到服务器





关于风控:
新账号被风控纯属正常现象，可能会导致群聊信息无法发送,但是私聊不影响,就算换账号也无法完全避免被风控
解决方案:在一台固定的机器上把这个qq号用go-cqhttp客户端硬挂几天



注:
1. AI续写翻译插件需要在 ".env.prod" 内填写相应内容
2. setur18开启在data下 "r18list.txt" 填写群号,setu需要ban群聊在env内加setu_ban=["群聊号码1","群聊号码2"]
3. 颜值评分功能需要前往https://cloud.baidu.com/product/face 申请免费资源并创建应用,获取应用的API Key和Secret Key并对__init__.py中开头的两个常量进行替换

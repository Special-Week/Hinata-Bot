# Hinata

## How to start
1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `hinata/plugins` folder.
4. run your bot using `nb run` .
## Documentation

See [Docs](https://v2.nonebot.dev/)

声明一下:
本仓库储存的是本人的私人bot
99.9%的代码来自nonebot社区,自己写的大概只有0.1%不到   (°ー°〃)
不太会玩github,请多多担待


要是真的有路人看到的话就按照一下方式搭建
下面的方式搭建你不会学习到任何知识,我的建议是 (https://v2.nonebot.dev/) 从零开始学习搭建以及使用社区的插件再到自己写插件




以下为纯萌新搭建此bot教程:
测试环境为虚拟机上新安装的windows10 21h2
1. 安装python3(我自己用的是python 3.10.4)
2. Windows强烈建议安装好 C++ Build Tools 以及 Microsoft Visual C++ 2013 Redistributable Package
3. 双击 "换源安装一些依赖.bat" 安装一些必要的环境
4. 使用控制台cd到hinata文件夹目录(bot.py的那个),输入nb run或python bot.py运行bot
5. 进入go-cqhttp文件夹
6. 双击 "go-cqhttp.bat" 扫码并且登陆
7. 登陆失败就多试几次,本地端登不上就连接同一局域网登陆.
8. 服务器端登不上就本地先登,登上了把gocqhttp复制到服务器


注:
1. AI续写翻译插件需要在 ".env.prod" 内填写相应内容
2. setur18开启在data下 "r18list.txt" 填写群号

# Hinata简介
一只可爱,~~并且色情~~的QQ群聊bot

# 声明:
本仓库储存的是本人的私人bot

(大)部分插件来自nonebot2社区, 已写明链接, 详细用法请参考该插件仓库readme

部分插件版本比较旧, 可能和主页readme不太一样, 可以考虑自己更新或者自己悟

要是真的有路人看到的话就按照以下方式搭建

下面的方式搭建你不会学习到任何知识,我的建议是 (https://v2.nonebot.dev) 从零开始学习搭建以及使用社区的插件再到自己写插件

代码只要你想可以任意改


# 以下为纯萌新搭建此bot教程:
自备计算机基础知识

测试环境为虚拟机上新安装的windows10 21h2, Linux环境自备对应的go-cqhttp, 和一些插件需要的字体

    0. 点击右上角绿色的Code按钮, Download Zip下载bot本体 (256 MB, 抽签抽卡等图片资源占大头)
    1. 安装python3, 记得勾选Add to path(我自己用的是python 3.10.4, 但我推荐3.8.10或3.9.12, 下载链接: https://www.python.org/ftp/python/3.9.12/python-3.9.12-amd64.exe)
    2. Windows强烈建议安装好 Visual C++ Build Tools 以及 Microsoft Visual C++ 2013 Redistributable Package,C++ Build Tools可能不太好找,可以选择通过visual studio安装"使用C++的桌面开发"( ~~看不懂就跳过算了~~)
    3. 双击 "换源安装一些依赖.bat" 安装一些必要的环境, 等待安装完, 安装完后控制台会显示按任意键继续然后自动关闭
    4. 使用控制台(cmd或者powershell)cd到hinata文件夹目录(有bot.py的那个),输入nb run或python bot.py运行bot(不要关闭控制台)
    5. 进入go-cqhttp文件夹
    6. 双击 "go-cqhttp.bat" 扫码并且登陆(第一次登陆建议连接同一局域网, 或者手机开热点) ,账号登陆缓存为go-cqhttp文件夹下的session.token, 需要换号登陆删除即可
    7. 登陆失败就多试几次, 服务器端登不上就本地先登, 登上了把gocqhttp复制到服务器
    8. 两个控制台需要同时开着, gocqhttp是负责收发消息, bot是负责处理消息的
    

# 插件列表:
    cp              cp <攻> <受>
    leetspeak       火星文 | 蚂蚁文 | 翻转文字 | 故障文字
    setu            ^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?
    ai              智障回复
    Daily_epilepsy  每日发癫 | 发癫
    api_iyko        一些api, 指令有 [来点笑话, 来点彩虹屁, 我在人间凑数的日子, 来点土味情话, 来点逆天, 来点伤感语录, 60秒读世界, 今天节日, 降雨预报, coser
    bt              磁力搜索
    face_beauty     颜值评分, (注:颜值评分功能需要前往https://cloud.baidu.com/product/face 申请免费资源并创建应用,获取应用的API Key和Secret Key并对__init__.py中开头的两个常量进行替换)
    get_wife        选妃
    pcr_chara_name  公主连结角色 [xxx是谁] 例如: 但丁是谁
    pixiv_id        pixiv_id xxxx | pixiv_id xxxx-x
    status          服务器状态
    what_anime      识番
    yiyandingzhen   一眼丁真 | yydz
    random_essay    随机小作文 | 发病小作文
    abbrreply       缩写 (https://github.com/anlen123/nonebot_plugin_abbrreply)
    abstract        抽象 (https://github.com/CherryCherries/nonebot-plugin-abstract)
    caiyunai        续写 (https://github.com/MeetWq/nonebot-plugin-caiyunai)
    code            在线运行代码 (https://github.com/yzyyz1387/nonebot_plugin_code)
    color           根据RGB数值生成色图 (https://github.com/monsterxcn/nonebot-plugin-color)
    covid19_news    疫情查询 (https://github.com/Zeta-qixi/nonebot-plugin-covid19-news)
    crazy_Thursday  疯狂星期四 (https://github.com/KafCoppelia/nonebot_plugin_crazy_thursday)
    ddcheck         查成份 (https://github.com/MeetWq/nonebot-plugin-ddcheck)
    emojimix        emoji 合成器 (https://github.com/MeetWq/nonebot-plugin-emojimix)
    gamedraw        模拟抽卡 (https://github.com/HibiKier/nonebot_plugin_gamedraw)
    handle          猜成语 (https://github.com/MeetWq/nonebot-plugin-handle)
    hikarisearch    搜图 (https://github.com/MeetWq/nonebot-plugin-hikarisearch)
    leetcode2       力扣查询 (https://github.com/Nranphy/nonebot_plugin_leetcode2)
    logo            logo制作 (https://github.com/MeetWq/nonebot-plugin-logo)
    memes           表情包制作 (https://github.com/MeetWq/nonebot-plugin-memes)
    petpet          头像表情包制作 (https://github.com/MeetWq/nonebot-plugin-petpet)
    randomtkk       随机唐可可 (https://github.com/MinatoAquaCrews/nonebot_plugin_randomtkk)
    repeater        复读机 (https://github.com/ninthseason/nonebot-plugin-repeater)
    simplemusic     点歌 (https://github.com/MeetWq/nonebot-plugin-simplemusic)
    tarot           塔罗牌 (https://github.com/KafCoppelia/nonebot_plugin_tarot)
    translator      翻译插件 (https://github.com/Lancercmd/nonebot_plugin_translator)
    weather_lite    天气查询 (https://github.com/zjkwdy/nonebot_plugin_weather_lite)
    withdraw        撤回消息 (https://github.com/noneplugin/nonebot-plugin-withdraw)
    word_bank2      词库插件 (https://github.com/kexue-z/nonebot-plugin-word-bank2)
    wordle          猜单词游戏 (https://github.com/MeetWq/nonebot-plugin-wordle)


# 关于风控:
新账号被风控纯属正常现象，可能会导致群聊信息无法发送,但是私聊不影响,就算换账号也无法完全避免被风控

解决方案:在一台固定的机器上把这个qq号用go-cqhttp客户端硬挂几天

# 注:
  1. setur18开关的相关指令"add_r18 xxx"  "del_r18 xxx"  "r18名单"
  2. 颜值评分功能需要前往https://cloud.baidu.com/product/face 申请免费资源并创建应用,获取应用的API Key和Secret Key并对__init__.py中开头的两个常量进行替换
  3. 如果服务器是Windows server2012为了能使用cv2库则需要在<服务器管理器-添加角色和功能向导-功能>中安装桌面体验
  4. 功能相关建议稍微读一下src/plugin里面的每个插件源码中声明响应器部分
  
  
# Hinataの封号日记 (开始写于2022/6/28)
    2022/06/26   Hinita(一号机) 限制QQ登录(可解除)        理由: 涉嫌进行业务违规操作
    2022/06/27   Hinita(五号机) 限制QQ登录(封号七天)      理由: 涉嫌传播色情信息或组织相关活动
    2022/06/29   Hinita(三号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/04   Hinita(四号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/04   Hinita(一号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/04   Hinita(四号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动(一小时封了两次, 有内鬼)
    2022/07/05   Hinita(五号机) 限制QQ登录(可解除)        理由: 涉嫌进行业务违规操作
    2022/07/06   Hinita(五号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/06   Hinita(五号机) & Hinita(四号机)被风控, 手动发送消息也冒着大大的感叹号      原因未知   
    2022/07/08   Hinita(二号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/12   Hinita(三号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/14   Hinita(三号机) 限制QQ登录(可解除)        理由: 涉嫌传播色情信息或组织相关活动
    2022/07/17   Hinita(一号机) 限制QQ登录(封号一天)      理由: 涉嫌传播色情信息或组织相关活动
    2022/07/18   Hinita(五号机) 限制QQ登录(封号一天)      理由: 涉嫌传播色情信息或组织相关活动
    2022/07/18   Hinita(四号机) 限制QQ登录(封号一天)      理由: 涉嫌传播色情信息或组织相关活动

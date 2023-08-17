# youth-version-of-setu4

内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(随机修改左上角一颗像素点) (tx好像改了算法, 作用不明显了)


### 目前数据库去除unavailable, 共81358条记录

ghs比较纯粹, 只有一般的权限控制, 相比完整版功能简单

安装方式:
    
    pip install youth-version-of-setu4
    
    记得nonebot.load_plugin("youth-version-of-setu4")
    
    有能力尽量从本仓库clone, 因为pypi不一定最新

## env 配置项

>以下配置项均可不填，插件会按照默认值读取

|config             |type            |default|example                          |usage                 |
|-------------------|----------------|-------|---------------------------------|----------------------|
|setu_cd            |int             |20     |setu_cd = 30                     |setu的cd              |
|setu_withdraw_time |int             |100    |setu_withdraw_time = 30          |setu撤回时间           |
|setu_max_num       |int             |10     |setu_max_num = 20                |setu一次性最大数量     |
|setu_save          |str             |None   |setu_save = './data/setu4/img'   |setu时候保存到本地的路径  可用绝对路径|

setu_save保存后下一次调用碰到这个setu就不需要再下载


一般无需科学上网, 确认一下图片代理是否可用:   

    一些也许可用的pixiv代理, 用来填入env的setu_proxy变量: "i.pixiv.re" , "sex.nyan.xyz" , "px2.rainchan.win" , "pximg.moonchan.xyz" , "piv.deception.world" , "px3.rainchan.win" , "px.s.rainchan.win" , "pixiv.yuki.sh" , "pixiv.kagarise.workers.dev" , "pixiv.kagarise.workers.dev"
    
    Example:
    
        数据库给的url为: https://i.pixiv.re/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg
    
        有些代理可能会暂时不可用, 可以用来换成可用的代理, 比如px2.rainchan.win
    
        即: https://px2.rainchan.win/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg
    
        能正常访问即可用, 详情请看下文superuser指令


​    

## 插件指令

setu命令:

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 填了就是r18, 不填则不是  (私聊生效, 群聊除非add_r18, 不然视为false)
    
    关键词: 任意 (可不填)
    
    参考:   
    
        setu 10张 r18 白丝
        
        setu 10张 白丝
        
        setu r18 白丝
        
        setu 白丝
        
        setu
        
        (空格可去掉, 多tag用空格分开 eg:setu 白丝 loli)



superuser指令:

    r18名单: 查看r18有哪些群聊或者账号
    
    add_r18 xxx: 添加r18用户/群聊
    
    del_r18 xxx: 移除r18用户
    
    disactivate | 解除禁用 xxx: 恢复该群的setu功能
    
    ban_setu xxx: 禁用xxx群聊的色图权限
    
    setu_proxy 更换setu代理(当默pixiv.re不可用时), 先发送setu_proxy, 然后他会给你一个魔方阵, 自己选择用哪个, 也可以用自己的



群主/管理员指令:

    ban_setu: 禁用当前群聊功能, 解除需要找superuser



其他指令:

    setu_help


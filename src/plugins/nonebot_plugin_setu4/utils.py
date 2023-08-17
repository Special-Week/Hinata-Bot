import json
from .config import config

class Utils:
    def __init__(self) -> None:
        self.config = json.load(open(config.config_file, 'r', encoding="utf-8"))
        """
        json结构:
        {
            "r18list": [
                "123456789",
                "987654321"
            ],
            "banlist": [
                "123456789",
                "987654321"
            ],
            "setu_proxy":"i.pixiv.re"
        }
        """
        self.r18list = self.config["r18list"]
        self.banlist = self.config["banlist"]


    def write_configjson(self) -> None:
        """写入json"""
        with open(config.config_file, 'w', encoding="utf-8") as fp:
            json.dump(self.config, fp, ensure_ascii=False)


    def read_proxy(self) -> str:
        """读取代理"""
        return self.config["setu_proxy"]


    def write_proxy(self, proxy: str) -> None:
        """写入代理"""
        self.config["setu_proxy"] = proxy
        self.write_configjson()


    def to_json(
        self, 
        msg, 
        uin: str,
        name: str
    ) -> dict:
        """转换为dict, 转发消息用"""
        return {
            'type': 'node',
            'data': {
                'name': name,
                'uin': uin,
                'content': msg
            }
        }
    

utils = Utils()




setu_help = """命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
参数可接r18, 数量, 关键词
eg:         
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
setu_proxy: 更换setu代理(会提示一些允许可用的代理)

群主/管理员:
ban_setu: 禁用当前群聊功能, 解除需要找superuser"""
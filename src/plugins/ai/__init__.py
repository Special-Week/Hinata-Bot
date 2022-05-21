import random
from nonebot import on_keyword
from nonebot.rule import to_me
from nonebot.plugin.on import on_command, on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
import io
from PIL import Image
from pathlib import Path
import requests
import os
from pathlib import Path
NICKNAME: str = "Hinata"
from typing import Union
try:
    import ujson as json
except ModuleNotFoundError:
    import json
random.seed(1)

NICKNAME: str = "Hinata"
MASTER: str = "星野日向_Official"

attack_sendmessage = [
    "不理你啦，baka",
    "你再这样咱就不理你了（＞д＜）",
    "我给你一拳",
    "不理你啦！バーカー",
    "baka！再这样不理你了！",
    "你在说什么呀，再这样，咱就不理你了！",
]
attack = on_keyword(["憨批", "傻逼", "sb", "SB", "笨蛋", "你妈", "nm",
                    "憨憨", "狗","儿子","爹","爸爸", "猪", "甘霖娘"], rule=to_me(), block=True, priority=98)
@attack.handle()
async def handle_receive():
    img = Image.open(Path(os.path.join(os.path.dirname(__file__), "resource")) / "1.jpg").convert('RGB')
    output = io.BytesIO()
    img.save(output, format='PNG')
    base64_data = output.getvalue()
    await attack.send(message=f"\n{random.choice(attack_sendmessage)}"+MessageSegment.image(base64_data), at_sender=True)


NICKNAME: str = "Hinata"
MASTER: str = "星野日向_Official"
anime_data = json.load(open(Path(os.path.join(os.path.dirname(__file__), "resource")) / "data.json", "r", encoding="utf8"))

Anime = on_message(rule=to_me(), priority=99)

def get_message_text(data: Union[str, Message]) -> str:
    """
    说明：
        获取消息中 纯文本 的信息
    参数：
        :param data: event.json()
    """
    result = ""
    if isinstance(data, str):
        data = json.loads(data)
        for msg in data["message"]:
            if msg["type"] == "text":
                result += msg["data"]["text"].strip() + " "
        return result.strip()
    else:
        for seg in data["text"]:
            result += seg.data["text"] + " "
    return result

def hello() -> str:
    """
    一些打招呼的内容
    """
    result = random.choice(
        (
            "哦豁？！",
            "你好！Ov<",
            f"库库库，呼唤{NICKNAME}做什么呢",
            "我在呢！",
            "呼呼，叫俺干嘛",
        )
    )
    return result

async def get_chat_result(text: str, user_id: int, nickname: str) -> str:
    if len(text) < 6:
        keys = anime_data.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(anime_data[key]).replace("你", nickname)

@Anime.handle()
async def _(bot: Bot, event: MessageEvent):
    msg = get_message_text(event.json())
    if "CQ:xml" in str(event.get_message()):
        return
    # 打招呼
    if (not msg) or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await Anime.finish(hello())
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    result = await get_chat_result(msg, event.user_id, nickname)
    if result == None:
        await Anime.finish(Message(str(requests.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}").json()["content"]).replace("林欣",MASTER).replace("{br}","\n").replace("贾彦娟",MASTER).replace("周超辉",MASTER).replace("鑫总",MASTER).replace("张鑫",MASTER).replace("菲菲",NICKNAME).replace("dn",MASTER).replace("1938877131","2749903559").replace("小燕",NICKNAME)))
    await Anime.finish(Message(result))



help = on_command("!help", aliases={"！help", "!帮助", "！帮助"},block=True)
@help.handle()
async def handle_receive():
    img = Image.open("data/help.png").convert('RGB')
    output = io.BytesIO()
    img.save(output, format='PNG')
    base64_data = output.getvalue()
    await help.send(MessageSegment.image(base64_data), at_sender=True)

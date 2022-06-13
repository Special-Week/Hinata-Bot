from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
import random
from nonebot import on_keyword, on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.params import CommandArg
from pathlib import Path
import requests
import os
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json
cdTime = 7200
data_dir = "./data/sb_CD"
NICKNAME: str = "Hinata"
MASTER: str = "星野日向_Official"


attack_sendmessage = [
    "不理你啦，baka",
    "我给你一拳",
    "不理你啦！バーカー",
    "baka！不理你了！",
    "你在说什么呀，咱就不理你了！",
]
# 有人骂了我家bot就不理他两小时,优先级98
attack = on_keyword(["憨批", "傻逼", "sb", "SB", "笨蛋", "你妈", "nm",
                    "憨憨", "狗", "儿子", "爹", "爸爸", "猪", "甘霖娘"], rule=to_me(), block=True, priority=98)


@attack.handle()
async def handle_receive(event: MessageEvent):
    img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "1.jpg"
    qid = event.get_user_id()
    data = read_json()
    mid = event.message_id
    write_json(qid, event.time, mid, data)
    await attack.send(message=f"{random.choice(attack_sendmessage)}"+MessageSegment.image(img), at_sender=True)

# 提前处理消息,用于阻断


@event_preprocessor
async def event_preblock_sb(event: MessageEvent, bot: Bot):
    if not event.get_user_id() in bot.config.superusers:
        qid = event.get_user_id()
        data = read_json()
        try:
            cd = event.time - data[qid][0]
        except Exception:
            cd = cdTime + 1
        if cd > cdTime:
            logger.info(f'当前事件正常')
            return
        blockreason = "这货骂了我家bot"
        if blockreason:
            logger.info(f'当前事件已阻断，原因：{blockreason}')
            raise IgnoredException(blockreason)

# 载入词库
anime_data = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource")) / "data.json", "r", encoding="utf8"))


# 回复一些打招呼的内容
def hello():
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

# 从字典里返还消息


async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 6:
        keys = anime_data.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(anime_data[key]).replace("你", nickname)

# 优先级99
anime = on_command("", rule=to_me(), priority=99)


@anime.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    # 获取消息文本
    msg = msg.extract_plain_text()

    print(msg)
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
        await anime.finish(hello())
    # 群聊事件
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用qingyunke
    if result == None:
        await anime.finish(Message(str(requests.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}").json()["content"]).replace("林欣", MASTER).replace("{br}", "\n").replace("贾彦娟", MASTER).replace("周超辉", MASTER).replace("鑫总", MASTER).replace("张鑫", MASTER).replace("菲菲", NICKNAME).replace("dn", MASTER).replace("1938877131", "2749903559").replace("小燕", NICKNAME)))
    await anime.finish(Message(result))


# help响应器
help = on_command("!help", aliases={
                  "！help", "!帮助", "！帮助", "help", "帮助"}, block=True)

# 发送help处理操作


@help.handle()
async def handle_receive():
    img = Path(os.path.join(os.path.dirname(
        __file__), "resource")) / "help.png"
    await help.send(MessageSegment.image(img), at_sender=True)


def read_json() -> dict:
    try:
        with open(data_dir + "usercd.json", "r") as f_in:
            data = json.load(f_in)
            f_in.close()
            return data
    except FileNotFoundError:
        try:
            import os

            os.makedirs(data_dir)
        except FileExistsError:
            pass
        with open(data_dir + "usercd.json", mode="w") as f_out:
            json.dump({}, f_out)

        return {}


def write_json(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()

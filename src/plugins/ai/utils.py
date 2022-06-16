from pathlib import Path
import os
import random
data_dir = "./data/sb_CD"
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from typing import Union
from nonebot.adapters.onebot.v11 import Message

NICKNAME: str = "Hinata"      # bot的nickname,可以换成你自己的
MASTER: str = "星野日向_Official"  # bot的主人名称,也可以换成你自己的
# 载入词库(这个词库有点涩)
anime_data = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource")) / "data.json", "r", encoding="utf8"))


# read_json的工具函数
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

# write_json的工具函数
def write_json(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()


# remove_json的工具函数
def remove_json(qid: str):
    with open(data_dir + "usercd.json", "r") as f_in:
        data = json.load(f_in)
        f_in.close()
    data.pop(qid)
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()


attack_sendmessage = [
    "不理你啦，baka",
    "我给你一拳",
    "不理你啦！バーカー",
    "baka！不理你了！",
    "你在说什么呀，咱就不理你了！",
]


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


def get_message_text(data: Union[str, Message]) -> str:
    # 获取on_message的纯文本消息
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


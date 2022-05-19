from typing import List, Union
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from nonebot import on_command
from nonebot.params import Arg
import requests
from nonebot.typing import T_State
try:
    import ujson as json
except ModuleNotFoundError:
    import json
import time
__zx_plugin_name__ = "识番"
__plugin_usage__ = """
usage：
    api.trace.moe 以图识番
    指令：
        识番 [图片]
""".strip()
__plugin_des__ = "以图识番"
__plugin_cmd__ = ["识番 [图片]"]
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.1
__plugin_author__ = "HibiKier"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["识番"],
}


what_anime = on_command("识番", priority=5, block=True)

def get_message_img(data: Union[str, Message]) -> List[str]:
    """
    说明：
        获取消息中所有的 图片 的链接
    参数：
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        data = json.loads(data)
        for msg in data["message"]:
            if msg["type"] == "image":
                img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list

@what_anime.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    img_url = get_message_img(event.json())
    if img_url:
        state["img_url"] = img_url[0]



@what_anime.got("img_url", prompt="虚空识番？来图来图GKD")
async def _(bot: Bot, event: MessageEvent, state: T_State, img_url: Message = Arg("img_url")):
    img_url = get_message_img(img_url)
    if not img_url:
        await what_anime.reject_arg("img_url", "发送的必须是图片！")
    img_url = img_url[0]
    await what_anime.send("开始识别.....")
    anime_data_report = await get_anime(img_url)
    if anime_data_report:
        await what_anime.send(anime_data_report, at_sender=True)
    else:
        await what_anime.send(f"没有寻找到该番剧，果咩..", at_sender=True)


async def get_anime(anime: str) -> str:
    s_time = time.time()
    url = "https://api.trace.moe/search?anilistInfo&url={}".format(anime)
    try:
        anime_json = requests.get(url).json()
        if not anime_json["error"]:
            if anime_json == "Error reading imagenull":
                return "图像源错误，注意必须是静态图片哦"
            repass = ""
            # 拿到动漫 中文名
            for anime in anime_json["result"][:5]:
                synonyms = anime["anilist"]["synonyms"]
                for x in synonyms:
                    _count_ch = 0
                    for word in x:
                        if "\u4e00" <= word <= "\u9fff":
                            _count_ch += 1
                    if _count_ch > 3:
                        anime_name = x
                        break
                else:
                    anime_name = anime["anilist"]["title"]["native"]
                episode = anime["episode"]
                from_ = int(anime["from"])
                m, s = divmod(from_, 60)
                similarity = anime["similarity"]
                putline = "[ {} ][{}][{}:{}] 相似度:{:.2%}".format(
                    anime_name,
                    episode if episode else "?",
                    m,
                    s,
                    similarity,
                )
                repass += putline + "\n"
            return f"耗时 {int(time.time() - s_time)} 秒\n" + repass[:-1]
        else:
            return f'访问错误 error：{anime_json["error"]}'
    except Exception as e:
        return "发生了奇怪的错误，那就没办法了，再试一次？"



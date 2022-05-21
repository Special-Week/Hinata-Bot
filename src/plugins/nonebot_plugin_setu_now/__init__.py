import random
from re import I
import asyncio
import nonebot
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import State
from nonebot.typing import T_State
from .get_data import get_setu
from .json_manager import read_json, remove_json, write_json
from .setu_message import setu_sendcd, setu_sendmessage


NICKNAME = "Hinata"
try:
    cdTime = nonebot.get_driver().config.setu_cd
except:
    cdTime = 0

try:
    banlist = nonebot.get_driver().config.setu_ban
except:
    banlist = []

try:
    withdraw_time = nonebot.get_driver().config.setu_withdraw_time
except:
    withdraw_time = 60


setu = on_regex(
    r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?(r18)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
    priority=1,
    block=True
)


@setu.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    global mid
    args = list(state["_matched_groups"])
    r18flag = args[1]
    key = args[2]
    qid = event.get_user_id()
    mid = event.message_id
    sid = event.get_session_id()
    for session_id in banlist:
        if session_id in sid:
            await setu.finish("涩图功能已在此会话中禁用！")
    data = read_json()
    try:
        cd = event.time - data[qid][0]
    except Exception:
        cd = cdTime + 1
    try:
        r18list = []
        fp = open('./data/r18list.txt')
        while True:
            line = fp.readline()
            if not line:
                break
            r18list.append(line.strip("\n"))
    except:
        r18list = nonebot.get_driver(
        ).config.r18_list if nonebot.get_driver().config.r18_list else []

    r18 = True if (isinstance(event, PrivateMessageEvent)
                   and r18flag) else False
    if not r18:
        for groubnumber in r18list:
            if groubnumber in sid:
                r18 = (True if (r18flag) else False)

    if key == "":
        flagLog = "\nR18 == "+str(r18)+"\n"+"keyword == NULL"+str(key)+"\n"
    else:
        flagLog = "\nR18 == "+str(r18)+"\n"+"keyword == "+str(key)+"\n"

    logger.info(f"key={key},r18={r18}")

    if (
        cd > cdTime
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):
        write_json(qid, event.time, mid, data)
        pic = await get_setu(key, r18)
        if pic[2]:
            try:
                message = f"{random.choice(setu_sendmessage)}{flagLog}" + \
                    Message(pic[1])+Message(pic[0])
                if isinstance(event, PrivateMessageEvent):
                    setu_msg_id = await setu.send(message)
                else:
                    messagesss = [to_json(msg, NICKNAME, bot.self_id)
                                  for msg in message]
                    setu_msg_id = await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=messagesss)
                setu_msg_id = setu_msg_id['message_id']
            except ActionFailed as e:
                logger.warning(e)
                remove_json(qid)
                await setu.finish(
                    message=Message(f"消息被风控，图发不出来\n{pic[1]}\n这是链接\n{pic[3]}"),
                    at_sender=True,
                )

        else:
            remove_json(qid)
            await setu.finish(pic[0] + pic[1])

    else:
        time_last = cdTime - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

        await setu.send(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}", at_sender=True)

        # 自动撤回涩图
    if withdraw_time != 0:
        if r18:
            try:
                await asyncio.sleep(40)
                await bot.delete_msg(message_id=setu_msg_id)
            except:
                pass
        else:
            try:
                await asyncio.sleep(withdraw_time)
                await bot.delete_msg(message_id=setu_msg_id)
            except:
                pass


def to_json(msg, name: str, uin: str):
    return {
        'type': 'node',
        'data': {
            'name': name,
            'uin': uin,
            'content': msg
        }
    }

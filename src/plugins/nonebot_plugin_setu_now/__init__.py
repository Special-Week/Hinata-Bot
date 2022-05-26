import random
from re import I
import asyncio
import nonebot
from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Message,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageSegment
)
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import State
from nonebot.typing import T_State
from .get_data import get_setu
from .json_manager import read_json, remove_json, write_json, to_json
from .setu_message import setu_sendcd, setu_sendmessage
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

# setu cd,可在env设置,默认20s,类型int
try:
    cdTime = nonebot.get_driver().config.setu_cd
except:
    cdTime = 20

# setu_ban名单,可在env设置,类型string列表
try:
    banlist = nonebot.get_driver().config.setu_ban
except:
    banlist = []

# 撤回时间,可在env设置,默认100s,类型int
try:
    withdraw_time = nonebot.get_driver().config.setu_withdraw_time
except:
    withdraw_time = 100

# 先读一读试试
try:
    fp = open('./data/r18list.txt')
    fp.close()
# 没有的话咱就新建
except:
    fp = open('./data/r18list.txt', 'w')
    fp.write("114514\n")
    fp.close()


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
    # 判断该群聊setu功能是否被禁用
    for session_id in banlist:
        if session_id in sid:
            await setu.finish("涩图功能已在此会话中禁用！")
    data = read_json()
    try:
        cd = event.time - data[qid][0]
    except Exception:
        cd = cdTime + 1

    # 读取r18列表
    r18list = []
    fp = open('./data/r18list.txt')
    while True:
        line = fp.readline()
        if not line:
            break
        r18list.append(line.strip("\n"))

    # 先判断r18flag和私聊是不是都是True进行赋值
    r18 = True if (isinstance(event, PrivateMessageEvent)
                   and r18flag) else False
    # 如果r18是false的话在进行r18list判断
    if not r18:
        for groubnumber in r18list:
            if groubnumber in sid:
                r18 = (True if (r18flag) else False)

    if key == "":
        flagLog = "\nR18 == "+str(r18)+"\n"+"keyword == NULL"+str(key)+"\n"
    else:
        flagLog = "\nR18 == "+str(r18)+"\n"+"keyword == "+str(key)+"\n"

    logger.info(f"key={key},r18={r18}")       # 控制台输出

    # cd判断,superusers无视cd
    if (
        cd > cdTime
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):
        write_json(qid, event.time, mid, data)
        pic = await get_setu(key, r18)
        if pic[2]:
            try:
                message = f"{random.choice(setu_sendmessage)}{flagLog}" + \
                    Message(pic[1])+MessageSegment.image(pic[0])
                # 判断是否是私聊,是直接发送
                if isinstance(event, PrivateMessageEvent):
                    setu_msg_id = await setu.send(message)
                # 群聊,以转发的形式发送
                elif isinstance(event,GroupMessageEvent):
                    messagesss = [to_json(msg, "setu-bot", bot.self_id)
                                  for msg in message]
                    setu_msg_id = await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=messagesss)
                # setu_msg_id后面撤回需要用
                setu_msg_id = setu_msg_id['message_id']
            # 发送失败,抛出异常
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
    # cd还没过的情况
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

        # 自动撤回涩图,r18图片则40s撤回,全年龄按照设置给的withdraw_time撤回
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


# r18列表添加用的,权限SUPERSUSER
addr18list = on_command("add_r18", permission=SUPERUSER, block=True)


@addr18list.handle()
async def _(arg: Message = CommandArg()):
    # 获取消息文本
    msg = arg.extract_plain_text().strip().split()[0]
    # 写入文件
    with open("data/r18list.txt", "a") as f:
        f.write(msg + "\n")
    fp.close()
    await addr18list.finish("ID:"+msg+"添加成功")


# r18列表删除用的,权限SUPERSUSER
del_r18list = on_command("del_r18", permission=SUPERUSER, block=True)


@del_r18list.handle()
async def _(arg: Message = CommandArg()):
    # 获取消息文本
    msg = arg.extract_plain_text().strip().split()[0]
    # 写入文件
    file = open("data/r18list.txt")
    lines = file.readlines()
    # 找到msg在lines的位置
    for i in range(len(lines)):
        if (msg+'\n') == lines[i]:
            del lines[i]
            break
    file.close()
    file_new = open("data/r18list.txt", 'w')
    # 将删除行后的数据写入文件
    file_new.writelines(lines)
    file_new.close()
    await del_r18list.finish("ID:"+msg+"删除成功")


get_r18list = on_command("r18名单", permission=SUPERUSER, block=True)


@get_r18list.handle()
async def _():
    r18list = []
    fp = open('./data/r18list.txt')
    while True:
        line = fp.readline()
        if not line:
            break
        r18list.append(line.strip("\n"))
    fp.close()
    await get_r18list.finish("R18名单：\n" + str(r18list))

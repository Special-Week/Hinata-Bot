from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
import random
from nonebot.plugin.on import on_keyword, on_command, on_message
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from .utils import *
from nonebot.params import CommandArg
from pathlib import Path
import requests
import os
from pathlib import Path
cdTime = 21600   # 这个是有人骂bot的时候ban的CD, 单位秒,可以自己改


# 响应器1, 有人骂了我家bot就不理他六小时, superuser除外(信息存在bot目录"data/sb_CDusercd.json"里面,可以删掉他提前解除)
# 判断方法:艾特了bot句子中包含以下关键词就触发, 可能会误触? 不管了, 响应器优先级50
attack = on_keyword(["傻逼", "sb", "SB", "你妈", "nm",
                     "狗", "儿子", "爹", "爸爸", "猪"], rule=to_me(), block=True, priority=50)
# 响应器2, 优先级60,条件:艾特bot就触发
ai = on_message(rule=to_me(), priority=99)
# 响应器3, 用来移除bot不理人的操作, 传入的参数是QQ号
remove_CD = on_command("remove_sb", permission=SUPERUSER, block=True)


@attack.handle()
async def handle_receive(event: MessageEvent):
    img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "1.jpg"
    qid = event.get_user_id()
    data = read_json()
    mid = event.message_id
    # 写入json,记录时间和id
    write_json(qid, event.time, mid, data)
    await attack.send(message=f"{random.choice(attack_sendmessage)}"+MessageSegment.image(img), at_sender=True)

# 提前处理消息,用于阻断


@event_preprocessor
async def event_preblock_sb(event: MessageEvent, bot: Bot):
    # 如果不是超级用户, 执行以下操作
    if not event.get_user_id() in bot.config.superusers:
        qid = event.get_user_id()
        data = read_json()
        try:
            cd = event.time - data[qid][0]
        except Exception:
            cd = cdTime + 1
        if cd > cdTime:
            return
        blockreason = "这货骂了我家bot"
        if blockreason:
            logger.info(f'当前事件已阻断，原因：{blockreason}')
            raise IgnoredException(blockreason)


@ai.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = get_message_text(event.json())
    if "CQ:xml" in str(event.get_message()):
        return
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
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
        await ai.finish(hello())
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用qingyunke获取智能回复
    if result == None:
        # 这个api好像问道主人或者他叫什么名字会返回私活,这里replace掉部分
        await ai.finish(Message(str(requests.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}").json()["content"]).replace("林欣", MASTER).replace("{br}", "\n").replace("贾彦娟", MASTER).replace("周超辉", MASTER).replace("鑫总", MASTER).replace("张鑫", MASTER).replace("菲菲", NICKNAME).replace("dn", MASTER).replace("1938877131", "2749903559").replace("小燕", NICKNAME)))
    await ai.finish(Message(result))


@remove_CD.handle()
async def _(msg: Message = CommandArg()):
    # 获取消息文本
    qid = msg.extract_plain_text()
    boolean = False
    # 我他妈也想直接try一下完事, 不知道为什么那样的话try和except全执行了, 焯
    try:
        remove_json(qid)
        boolean = True
    except:
        pass
    if boolean:
        await remove_CD.finish(f"ID:{qid}CD已清除, 下次别骂bot了")
    else:
        await remove_CD.finish(f"{NICKNAME}记忆里没有这号人欸")

    
    
    
    
    
    
    

# help响应器
help = on_command("!help", aliases={
                  "！help", "!帮助", "！帮助", "help", "帮助"}, block=True)

# 发送help处理操作

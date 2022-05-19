from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment
import asyncio
withdraw_time = 60


coser = on_regex("^(cos|COS|coser|括丝)$", priority=5, block=True)
url = "https://api.iyk0.com/cos"

@coser.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        msg_id = await coser.send(MessageSegment.image(url))
        msg_id = msg_id['message_id']
         # 自动撤回
        await asyncio.sleep(withdraw_time)
        await bot.delete_msg(message_id=msg_id)
    except:
        await coser.send("出错了!你来给大家整点")

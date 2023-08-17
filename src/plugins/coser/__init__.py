from random import choice

from nonebot import on_regex
from nonebot.adapters.onebot.v11.message import MessageSegment

coser = on_regex("^(cos|COS|coser|括丝)$", priority=5, block=True)
url = ["https://imgapi.cn/cos.php"]

@coser.handle()
async def _():
    try:
        await coser.send(MessageSegment.image(choice(url)))
    except Exception as e:
        await coser.send(f"出错了! 出错信息: {repr(e)}")

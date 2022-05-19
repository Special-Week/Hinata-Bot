from re import RegexFlag

try:
    from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
except ImportError:
    from nonebot.adapters.cqhttp import Bot, MessageSegment
    from nonebot.adapters.cqhttp.event import MessageEvent

from nonebot import on_regex
from nonebot.typing import T_State

from .data_source import gnrtImg

# zero2max = r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])"
color = on_regex(
    r"^(!色图|color)?\s*((#[a-f0-9]{6})|((25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\s+(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\s+(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])))$",
    flags=RegexFlag.IGNORECASE, block=True, priority=13
)


@color.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if state["_matched_groups"][2]:
        c = state["_matched_groups"][2]
    elif state["_matched_groups"][3]:
        c = state["_matched_groups"][4:7]
    else:
        await color.finish("奇怪的颜色增加了呢！")
    res = await gnrtImg(c)
    if res[0] == "b":  # "base64://"
        await color.finish(message='哎呦主人这个好色哦' + MessageSegment.image(res))
    else:
        await color.finish(message='哎呦主人这个好色哦' + res)

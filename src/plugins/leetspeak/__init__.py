from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .data_source import get_text, commands





async def handle(matcher: Type[Matcher], type: str, text: str):
    res = await get_text(type, text)
    if res:
        await matcher.finish(res)
    else:
        await matcher.finish("出错了，请稍后再试")


def create_matchers():
    def create_handler(type: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            text = msg.extract_plain_text().strip()
            if text:
                await handle(matcher, type, text)

        return handler

    for type, params in commands.items():
        matcher = on_command(
            f"{type}text", aliases=params["aliases"], block=True, priority=5
        )
        matcher.append_handler(create_handler(type))


create_matchers()

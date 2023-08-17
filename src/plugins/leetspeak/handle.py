import math
import random

from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .bug import bug_code, bug_level
from .flip import flip_table
from .hxw import encharhxw, enchars, ftw, hxw, jtw


class LeetSpeak:
    def __init__(self) -> None:
        ...

    async def hxw_text(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()
        if msg == "" or msg.isspace():
            return
        await matcher.send(await self.get_hxw_text(msg))

    async def ant_text(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()
        if msg == "" or msg.isspace():
            return
        await matcher.send(await self.get_ant_text(msg))

    async def flip_text(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()
        if msg == "" or msg.isspace():
            return
        await matcher.send(await self.get_flip_text(msg))


    async def bug_text(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()
        if msg == "" or msg.isspace():
            return
        await matcher.send(await self.get_bug_text(msg))
        

    async def get_hxw_text(self, text: str) -> str:
        result = ""
        for s in text:
            c = s
            if s in enchars:
                c = encharhxw[enchars.index(s)]
            elif s in jtw:
                c = hxw[jtw.index(s)]
            elif s in ftw:
                c = hxw[ftw.index(s)]
            result += c
        return result
    

    async def get_ant_text(self, text: str):
        return "".join(s + chr(1161) for s in text)



    async def get_flip_text(self, text: str):
        text = text.lower()
        return "".join(flip_table[s] if s in flip_table else s for s in text[::-1])


    async def get_bug_text(self, text: str):
        def bug(p, n):
            result = ""
            if isinstance(n, list):
                n = math.floor(random.random() * (n[1] - n[0] + 1)) + n[0]
            for _ in range(n):
                result += bug_code[p][int(random.random() * len(bug_code[p]))]
            return result

        level = 12
        u = bug_level[level]
        result = ""
        for s in text:
            result += s
            if s != " ":
                result += (
                    bug("mid", u["mid"])
                    + bug("above", u["above"])
                    + bug("under", u["under"])
                    + bug("up", u["up"])
                    + bug("down", u["down"])
                )
        return result






leetspeak = LeetSpeak()
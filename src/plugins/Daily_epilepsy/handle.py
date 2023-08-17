import json
import random
from pathlib import Path

from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent, Message,
                                         MessageEvent)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg


class Epilepsy:
    def __init__(self):
        module_path: Path = Path(__file__).parent
        self.post: list = (
            json.load(open(module_path / "post.json", "r", encoding="utf-8")))['post']

    async def get_at(self, bot: Bot, event: MessageEvent):
        if isinstance(event, GroupMessageEvent):
            msg = event.get_message()
            for msg_seg in msg:
                if msg_seg.type == "at":
                    return (await self.get_user_card(bot, event.group_id, int(msg_seg.data["qq"])))
        return None

    async def get_user_card(self, bot: Bot, group_id, qid) -> str:
        """返还用户nickname"""
        user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=qid)
        return user_info["card"] or user_info["nickname"]

    async def main(
        self,
        bot: Bot,
        event: MessageEvent,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        lucky_user = await self.get_at(bot,event)
        if lucky_user is None:
            msg = arg.extract_plain_text().strip()
            if msg == "" or msg.isspace():
                await matcher.finish("你要对谁发癫")
            random_post = random.choice(self.post).replace("阿咪", msg)
        else:
            if lucky_user == "" or lucky_user.isspace():
                await matcher.finish("你要对谁发癫")
            random_post = random.choice(self.post).replace("阿咪", lucky_user)

        await matcher.finish(random_post)
            


epilepsy = Epilepsy()
import json
import random
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher

from .txt2img import txt_to_img



class Essay:
    def __init__(self) -> None:
        self.essay_list = json.load(open(Path(__file__).parent / "data.json", "r", encoding="utf-8"))

    async def main(self, matcher: Matcher):
        data = random.choice(self.essay_list)
        essay_title = data["title"]
        await matcher.send(MessageSegment.text(f"标题: {essay_title}") + MessageSegment.image(await txt_to_img.txt_to_img(data["content"])))

essay = Essay()

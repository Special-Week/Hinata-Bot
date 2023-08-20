from io import BytesIO
from pathlib import Path
from typing import Dict

import numpy as np
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.params import CommandArg
from PIL import Image
from wordcloud import WordCloud

from .data_sheet import worddata
from .split_tense import split_tool

wordcloud_handle = on_command("词云", aliases={"wordcloud"}, priority=20, block=False)


@wordcloud_handle.handle()
async def wordcloud_handler(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    args = args.extract_plain_text()
    if "周" in args:
        data = worddata.get_week_data(group_id)
    elif "历史" in args:
        data = worddata.get_history_data(group_id)
    elif "月" in args:
        data = worddata.get_month_data(group_id)
    else:
        data = worddata.get_today_data(group_id)
    if not data:
        await wordcloud_handle.finish("暂时没有数据呢")
    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    if len(data) > 80:
        data = dict(list(data.items())[:80])
    img = await get_wordcloud_img(data)
    await wordcloud_handle.finish(MessageSegment.image(img))


async def rule(event: MessageEvent) -> bool:
    return (
        isinstance(event, GroupMessageEvent)
        and event.message.extract_plain_text() != ""
    )


split_word = on_message(
    block=False,
    rule=rule,
)


@split_word.handle()
async def split_word_handler(event: GroupMessageEvent):
    text = event.get_plaintext()
    data = await split_tool.split_tense(text)
    if data:
        worddata.insert_data(event.group_id, data)


async def get_wordcloud_img(data: Dict[str, int]) -> bytes:
    wordcloud = WordCloud(
        width=1200,
        height=1200,
        background_color="white",
        font_path=str(Path(__file__).parent / "fonts" / "SIMYOU.TTF"),
    ).generate_from_frequencies(data)
    image_array = np.array(wordcloud)
    pillow_image = Image.fromarray(image_array)
    pillow_image = pillow_image.convert("RGB")
    bytes_io = BytesIO()
    pillow_image.save(bytes_io, format="PNG")
    return bytes_io.getvalue()

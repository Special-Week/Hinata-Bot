from io import BytesIO
from pathlib import Path
from typing import Dict

import numpy as np
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from PIL import Image
from wordcloud import WordCloud

from .data_sheet import get_history_data, get_today_data, get_week_data, insert_data
from .split_tense import split_tool

wordcloud_handle = on_command("词云", aliases={"wordcloud"}, priority=20, block=False)


@wordcloud_handle.handle()
async def wordcloud_handler(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    args = args.extract_plain_text()
    if "周" in args:
        data = get_week_data(group_id)
    elif "历史" in args:
        data = get_history_data(group_id)
    else:
        data = get_today_data(group_id)
    if not data:
        await wordcloud_handle.finish("暂时没有数据呢")
    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    if len(data) > 80:
        data = dict(list(data.items())[:80])
    img = await get_wordcloud_img(data)
    await wordcloud_handle.finish(MessageSegment.image(img))


split_word = on_message(block=False)


@split_word.handle()
async def split_word_handler(event: GroupMessageEvent):
    text = event.get_plaintext()
    data = await split_tool.split_tense(text)
    if data:
        insert_data(event.group_id, data)


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

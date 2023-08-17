import os
import random
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.rule import to_me

audio_path = Path(__file__).parent / "resource"
audio_file_name = os.listdir(str(audio_path))

donxuelian = on_command("骂我",rule=to_me(), block=True)

@donxuelian.handle()
async def _():
    audio_name = random.choice(audio_file_name)
    audio = audio_path / audio_name
    await donxuelian.send(MessageSegment.record(audio))

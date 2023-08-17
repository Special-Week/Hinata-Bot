from nonebot import on_command

from .handle import pixiv_id

on_command("pixiv_id", block=True, handlers=[pixiv_id.main])

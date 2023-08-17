from nonebot import on_command
from .handle import epilepsy

on_command("每日发癫", aliases={"发癫"}, priority=5, block=True, handlers=[epilepsy.main])






from nonebot import on_command

from .handle import leetspeak

on_command("hxw", aliases={"火星文"}, priority=5, block=False, handlers=[leetspeak.hxw_text])
on_command("ant", aliases={"蚂蚁文"}, priority=5, block=False, handlers=[leetspeak.ant_text])
on_command("flip", aliases={"翻转文字"}, priority=5, block=False, handlers=[leetspeak.flip_text])
on_command("bug", aliases={"故障文字"}, priority=5, block=False, handlers=[leetspeak.bug_text])

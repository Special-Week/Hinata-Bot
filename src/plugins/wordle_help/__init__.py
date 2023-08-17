import contextlib

from nonebot import on_regex

from .handle import wordle_help

# 注册正则表达式, 优先级为10, 阻断式, 处理函数为wordle_help.main
on_regex(
    r'^(?=.*[a-zA-Z])(?=.*_)[a-zA-Z_]+(#(?=[a-zA-Z]+$)[a-zA-Z]*)?$',
    priority=10,
    block=True,
    handlers=[wordle_help.main]
)

with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata
    __plugin_meta__ = PluginMetadata(
        name="wordle_help",
        description="wordle游戏小助手",
        usage=r'^(?=.*[a-zA-Z])(?=.*_)[a-zA-Z_]+(#(?=[a-zA-Z]+$)[a-zA-Z]*)?$',
        type="application",
        homepage="https://github.com/Special-Week/Hinata-Bot/tree/main/src/plugins/wordle_help",
        supported_adapters={"~onebot.v11"},
        extra={
            'author':   'Special-Week',
            'version':  '0.0.1',
            'priority': 10,
        }
    )

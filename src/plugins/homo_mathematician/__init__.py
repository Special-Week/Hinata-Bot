import contextlib

from nonebot import on_command

from .handle import homo_number, lagrange_interpolation

with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata
    __plugin_meta__ = PluginMetadata(
        name="homo_mathematician",
        description="任何实数都用连续的114514通过加减乘除达成, 任给一组数据都能找出其内在规律(函数表达式)",
        usage=r'命令头: {lag, 找规律}  / {homonumber, 臭数字}  eg: 找规律 1 2 3 4 5 6 7 114514 1919810  / homonumber 2749903559',
        type="application",
        homepage="https://github.com/Special-Week/Hinata-Bot/tree/main/src/plugins/homo_mathematician",
        supported_adapters={"~onebot.v11"},
        extra={
            'author':   'Special-Week',
            'version':  '0.0.6',
            'priority': 10,
        }
    )



on_command(
    cmd = "homonumber", 
    block=True, 
    priority=10, 
    aliases={"臭数字"}, 
    handlers=[homo_number.main]
)

on_command(
    cmd = 'lag',
    block=True,
    priority=10,
    aliases={"找规律"},
    handlers=[lagrange_interpolation.main],
)

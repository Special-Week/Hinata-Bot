import contextlib
from typing import Any, Dict

from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Bot as Onev11Bot
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.message import event_preprocessor

from .main import status

driver = get_driver()

# 优先级10, 不向下阻断
server_status = on_command(
    "服务器状态",
    aliases={"状态", "status"},
    priority=10,
    block=False,
)


@event_preprocessor
async def _(event: MessageEvent) -> None:
    """依赖注入消息事件，如果是消息事件则将消息计数器加一"""
    bot_id = event.self_id
    status.receive_msg[bot_id] += 1


@driver.on_bot_connect
async def _(bot: Onev11Bot) -> None:
    """依赖注入 Bot 对象，给连接的机器人创建计数器"""
    bot_id = int(bot.self_id)
    if bot_id not in status.send_msg:
        status.send_msg[bot_id] = 0
        status.receive_msg[bot_id] = 0


@Bot.on_calling_api
async def _(bot: Bot, api: str, data: Dict[str, Any]) -> None:
    """钩子函数，如果调用的api是send则将消息计数器加一"""
    with contextlib.suppress(Exception):
        if "send" in api:
            bot_id = int(bot.self_id)
            status.send_msg[bot_id] += 1


@server_status.handle()
async def _(bot: Onev11Bot) -> None:
    """服务器状态命令处理函数"""
    login_info: Dict[str, Any] = await bot.get_login_info()
    await server_status.send(
        MessageSegment.image(
            await status.draw_img(login_info["user_id"], login_info["nickname"])
        )
    )


with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata

    __plugin_meta__ = PluginMetadata(
        name="status",
        description="获取服务器状态",
        usage=r'命令头：状态 | status | 服务器状态',
        type="application",
        homepage="https://github.com/Special-Week/Hinata-Bot/tree/main/src/plugins/status",
        supported_adapters={"~onebot.v11"},
        extra={
            "author": "Special-Week",
            "version": "0.0.1",
            "priority": 10,
            "block": False,
        },
    )

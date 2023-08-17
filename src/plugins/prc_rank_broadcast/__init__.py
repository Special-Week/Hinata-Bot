import contextlib
from typing import Dict, List, Union

import nonebot
from nonebot import get_driver, on_command, require
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .config import config
from .draw import drawtable
from .main import pcr_rank

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

rank = on_command("公会排名", priority=5, block=False)
is_open = on_command(
    "定时",
    aliases={"播报"},
    rule=pcr_rank.rule,
    priority=5,
    block=False,
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
)
add_group = on_command(
    "添加公会",
    aliases={"添加"},
    priority=5,
    block=False,
    permission=SUPERUSER,
)
del_group = on_command(
    "删除公会",
    aliases={"删除"},
    priority=5,
    block=False,
    permission=SUPERUSER,
)

clean_data = on_command(
    "清除排名数据",
    aliases={"清除排名"},
    priority=5,
    block=False,
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
)

@clean_data.handle()
async def _(event: GroupMessageEvent) -> None:
    gid = event.group_id
    if gid in pcr_rank.group.keys():
        name = pcr_rank.group[gid]
        pcr_rank.history_data[name] = []
        await pcr_rank.save_json()
        await clean_data.finish("清除成功")
    else:
        await clean_data.finish("未找到对应公会")


@add_group.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()) -> None:
    gid = event.group_id
    target = args.extract_plain_text()
    if not target:
        await add_group.finish("请在命令后接上公会名")
    resp = await pcr_rank.get_guild_rank(target)
    if isinstance(resp, str):
        await add_group.finish("获取公会排名失败, 添加不成功")
    else:
        pcr_rank.group[gid] = target
        await pcr_rank.save_config()
        await add_group.finish(f"添加成功, 获取到的信息为{resp}")


@del_group.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()) -> None:
    gid = event.group_id
    target = args.extract_plain_text()
    if not target:
        await del_group.finish("请在命令后接上公会名")
    if pcr_rank.group.get(gid) == target:
        del pcr_rank.group[gid]
        await pcr_rank.save_config()
        await del_group.finish("删除成功")
    else:
        await del_group.finish("删除失败, 未找到对应公会")


@is_open.handle()
async def _(event: GroupMessageEvent) -> None:
    original_message = event.raw_message
    if "关闭" in original_message or "取消" in original_message:
        config.guild_default_switch = False
        await is_open.finish("已关闭")
    elif "开启" in original_message or "打开" in original_message:
        config.guild_default_switch = True
        await is_open.send("已开启")
        await sched()


@rank.handle()
async def _(event: GroupMessageEvent) -> None:
    if event.group_id not in pcr_rank.group.keys():
        await rank.finish("config中未找到对应公会")

    group_name: str = pcr_rank.group[event.group_id]
    data: Union[str, List[Dict]] = await pcr_rank.get_guild_rank(group_name)
    if isinstance(data, str):
        await rank.finish("获取排名失败")
    pic = await drawtable.draw(data)
    message = MessageSegment.text("当前公会的排名") + MessageSegment.image(pic)
    gear_score_line: Union[str, List[Dict]] = await pcr_rank.get_gear_score_line()
    if isinstance(gear_score_line, list):
        target = await drawtable.draw(gear_score_line)
        message += MessageSegment.text("档线公会的排名") + MessageSegment.image(target)
    await rank.finish(message)


async def sched() -> None:
    if not config.guild_default_switch:
        return
    bot = nonebot.get_bot()
    data: Dict[int, Union[bytes, None]] = {}
    for _ in range(3):
        with contextlib.suppress(Exception):
            data = await pcr_rank.timed_crawling()
            break

    if data != {}:
        target: Union[bytes, None] = data.get(800000000)
        del data[800000000]
        for i, value in data.items():
            if value is not None:
                send_msg = MessageSegment.text("当前公会的排名"), MessageSegment.image(value)
                if target is not None:
                    send_msg += MessageSegment.text("档线公会的排名")
                    send_msg += MessageSegment.image(target)
                with contextlib.suppress(Exception):
                    name: str = pcr_rank.group[i]
                    image_bytes: bytes = await pcr_rank.draw_line_chart(
                        pcr_rank.history_data[name], name
                    )
                    send_msg += MessageSegment.text("排名趋势图")
                    send_msg += MessageSegment.image(image_bytes)
                with contextlib.suppress(Exception):
                    await bot.send_group_msg(group_id=i, message=send_msg)
    else:
        for key in pcr_rank.group.keys():
            await bot.send_group_msg(group_id=key, message="获取公会排名失败")


scheduler.add_job(sched, "interval", hours=config.interval, id="job_1")

driver = get_driver()


@driver.on_bot_connect
async def _() -> None:
    await sched()

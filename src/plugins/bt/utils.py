import asyncio
import contextlib
from typing import Any, Coroutine, List

import nonebot
from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from httpx import AsyncClient, Response
from loguru import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg


class BitTorrent:
    def __init__(self) -> None:
        """初始化一些变量, 用env拿到magnet_max_num参数"""
        try:
            self.max_num: int = nonebot.get_driver().config.magnet_max_num
        except Exception:
            self.max_num: int = 3

        self.magnet_url = "https://cili.site"

    async def main(
        self,
        bot: Bot,
        matcher: Matcher,
        event: MessageEvent,
        msg: Message = CommandArg(),
    ) -> None:
        """主函数, 用于响应命令"""
        keyword: str = msg.extract_plain_text()
        if not keyword:
            await matcher.finish("虚空搜索?来点车牌gkd")
        try:
            data: List[str] = await self.get_items(keyword)
        except Exception as e:
            await matcher.finish("搜索失败, 下面是错误信息:\n" + repr(e))
        # 如果搜索到了结果, 则尝试发送, 有些账号好像文本太长cqhttp会显示风控
        if not data:
            await matcher.finish("没有找到结果捏, 换个关键词试试吧")
        if isinstance(event, PrivateMessageEvent):
            await matcher.finish("\n".join(data))
        if isinstance(event, GroupMessageEvent):
            messages: list = [
                {
                    "type": "node",
                    "data": {
                        "name": "bot",
                        "uin": bot.self_id,
                        "content": i,
                    },
                }
                for i in data
            ]
            await bot.call_api(
                "send_group_forward_msg", group_id=event.group_id, messages=messages
            )

    async def get_items(self, keyword) -> List[str]:
        search_url: str = f"{self.magnet_url}/search?q={keyword}"
        async with AsyncClient() as client:
            try:
                resp: Response = await client.get(search_url)
            except Exception as e:
                print(repr(e))
                return [f"获取{search_url}失败， 错误信息：{repr(e)}"]
        soup = BeautifulSoup(resp.text, "lxml")
        tr: ResultSet[Any] = soup.find_all("tr")
        if not tr:
            return []
        a_list: list[Any] = [i.find_all("a") for i in tr]
        href_list: list[str] = [self.magnet_url + i[0].get("href") for i in a_list if i]
        maxnum: int = min(len(href_list), self.max_num)
        tasks: List[Coroutine] = [self.get_magnet(i) for i in href_list[:maxnum]]
        return await asyncio.gather(*tasks)

    async def get_magnet(self, search_url: str) -> str:
        try:
            async with AsyncClient() as client:
                resp: Response = await client.get(search_url)
            soup = BeautifulSoup(resp.text, "lxml")
            dl: Tag | NavigableString | None = soup.find(
                "dl", class_="dl-horizontal torrent-info col-sm-9"
            )
            h2: Tag | NavigableString | None = soup.find("h2", class_="magnet-title")
            if isinstance(dl, Tag) and isinstance(h2, Tag):
                dt: ResultSet[Any] = dl.find_all("dt")
                dd: ResultSet[Any] = dl.find_all("dd")
                target: str = (
                    f"标题 :: {h2.text}\n磁力链接 :: magnet:?xt=urn:btih:{dd[0].text}\n"
                )
                for i in range(1, min(len(dt), len(dd))):
                    dt_temp: str = (dt[i].text).split("\n")[0]
                    dd_temp: str = (dd[i].text).split("\n")[0]
                    if not dd_temp:
                        with contextlib.suppress(Exception):
                            dd_temp = (dd[i].text).split("\n")[1]
                    target += f"{dt_temp}: {dd_temp}\n"
                logger.info(f"{target}\n====================================")
                return target
            return f"获取{search_url}失败"
        except Exception as e:
            return f"获取{search_url}失败， 错误信息：{repr(e)}"


# 实例化
bittorrent = BitTorrent()

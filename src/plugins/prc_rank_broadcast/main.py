import json
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Union

from httpx import AsyncClient
from loguru import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import config
from .draw import drawtable
from .header import get_headers


class PcrRank:
    def __init__(self) -> None:
        self.module_path: Path = Path(__file__).parent
        self.data_file = "data.json"
        config_file = "config.json"
        if not (self.module_path / config_file).exists():
            with open(self.module_path / config_file, "w", encoding="utf-8") as f:
                temp_config: Dict[str, str] = {}
                json.dump(temp_config, f, ensure_ascii=False, indent=4)
        with open(self.module_path / config_file, "r", encoding="utf-8") as f:
            group: Dict[str, str] = json.load(f)
        self.group: Dict[int, str] = {int(k): v for k, v in group.items()}
        logger.info(f"监听的公会有{self.group}")
        if not self.group:
            config.guild_default_switch = False

        if not (self.module_path / self.data_file).exists():
            with open(self.module_path / self.data_file, "w", encoding="utf-8") as f:
                temp_data: Dict[str, List] = {}
                json.dump(temp_data, f, ensure_ascii=False, indent=4)
        with open(self.module_path / self.data_file, "r", encoding="utf-8") as f:
            self.history_data = json.load(f)
        self.font = str(self.module_path / "fonts" / "SIMYOU.TTF")
        self.api_url = "https://pcr-api.himaribot.com/clan/rankSearch"

    async def get_gear_score_line(self) -> Union[str, List[Dict]]:
        data = '{"name":"","leaderName":"","minRank":1,"maxRank":99999,"score":0,"page":0,"period":0,"maxPerPage":10,"fav":false,"onlyRank":true}'
        async with AsyncClient() as client:
            response = (await client.post(self.api_url, data=data, headers=get_headers())).json()  # type: ignore
        if response["statusCode"] != 200:
            return "挡位线获取失败"
        rank_data: List[Dict] = response["data"]["clans"]
        return rank_data

    async def get_guild_rank(self, guild_name: str) -> Union[str, List[Dict]]:
        data = '{"name":"guild_name","leaderName":"","minRank":1,"maxRank":99999,"score":0,"page":0,"period":0,"maxPerPage":10,"fav":false,"onlyRank":false}'
        async with AsyncClient() as client:
            response = (await client.post(self.api_url, headers=get_headers(), data=data.replace("guild_name", guild_name))).json()  # type: ignore
        if response["statusCode"] != 200:
            return "公会名获取失败"
        return "公会名获取失败" if response["data"] is None else response["data"]["clans"]

    async def timed_crawling(self) -> Dict[int, Union[None, bytes]]:
        pic_data: Dict[int, Union[None, bytes]] = {}
        for group_id, names in self.group.items():
            data: Union[str, List] = await self.get_guild_rank(names)
            if isinstance(data, str):
                pic_data[group_id] = None
                continue
            logger.info(f"获取{names}的排名成功")
            if names not in self.history_data:
                self.history_data[names] = []
            self.history_data[names].append(data[0]["rank"])
            pic_data[group_id] = await drawtable.draw(data)
        await self.save_json()
        gear_score: Union[str, List] = await self.get_gear_score_line()
        if isinstance(gear_score, str):
            pic_data[800000000] = None
        else:
            logger.info("获取档线公会的排名成功")
            pic_data[800000000] = await drawtable.draw(gear_score)
        return pic_data

    async def save_json(self) -> None:
        with open(self.module_path / self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.history_data, f, ensure_ascii=False, indent=4)

    async def save_config(self) -> None:
        with open(self.module_path / "config.json", "w", encoding="utf-8") as f:
            json.dump(self.group, f, ensure_ascii=False, indent=4)

    async def rule(self, event: GroupMessageEvent) -> bool:
        return event.group_id in self.group

    async def draw_line_chart(self, data: List[str], title: str) -> bytes:
        # 画折线图
        values = [int(i) for i in data]
        keys = title
        image = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        # ------------------------ 画一个框框 ------------------------

        image_new = Image.new("RGBA", (1920, 1080), (255, 255, 255, 0))
        draw_new = ImageDraw.Draw(image_new)
        draw_new.rectangle((420, 25, 1860, 1060), fill=(255, 255, 255, 220))
        image_new = image_new.filter(ImageFilter.GaussianBlur(radius=0.1))
        image.paste(image_new, (0, 0), image_new)

        # ------------------------ 画一个坐标轴 ------------------------

        draw.line((490, 1000, 1800, 1000), fill="black", width=2)
        draw.line((500, 50, 500, 1030), fill="black", width=2)
        maxnum_scale = max(values) / 9

        # ------------------------ 画一些虚线 ------------------------

        def draw_dotted_line(y):
            x_start, x_end = 500, 1800
            dash_length = 10
            gap_length = 5
            x = x_start
            while x < x_end:
                x_dash_end = min(x + dash_length, x_end)
                draw.line((x, y, x_dash_end, y), fill="black", width=1)
                x += dash_length + gap_length

        for i in range(10):
            draw_dotted_line(1000 - 950 * i / 10)

        maxnum_scale = (int(maxnum_scale / 20) + 1) * 20
        if maxnum_scale == 0:
            maxnum_scale = 20

        for i in range(10):
            draw.text(
                (450, 1000 - 950 * i / 10 - 10),
                str(maxnum_scale * i),
                fill="black",
                font=ImageFont.truetype(self.font, 20),
            )

        # ------------------------ 画折线图 ------------------------

        def draw_line_chart():
            x_start = 540
            x_gap = (1800 - x_start) / (len(values) - 1)
            x = x_start
            y = 1000 - 95 * (values[0] / maxnum_scale)
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="black", width=2)
            draw.text(
                (x - 20, y - 30),
                str(values[0]),
                fill="black",
                font=ImageFont.truetype(self.font, 32),
            )
            for i in range(1, len(values)):
                x_new = x_start + x_gap * i
                y_new = 1000 - 95 * (values[i] / maxnum_scale)
                draw.line((x, y, x_new, y_new), fill="black", width=2)
                x, y = x_new, y_new
                # 给每个点画个圆圈
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="black", width=2)
                # 在每个点上写上值
                draw.text(
                    (x - 20, y - 30),
                    str(values[i]),
                    fill="black",
                    font=ImageFont.truetype(self.font, 32),
                )

        draw_line_chart()

        # ------------------------ 画标题 ------------------------

        draw.text(
            (200, 600),
            keys,
            fill="black",
            font=ImageFont.truetype(self.font, 50),
            anchor="mm",
        )

        bytes_io = BytesIO()
        image.save(bytes_io, format="PNG")
        return bytes_io.getvalue()


pcr_rank = PcrRank()

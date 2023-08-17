from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont


class DrawTable:
    def __init__(self) -> None:
        self.module_path: Path = Path(__file__).parent
        self.font = str(self.module_path / "fonts" / "SIMYOU.TTF")
        self.slit: list[int] = [0, 89, 285, 450, 540, 740, 944]

    @staticmethod
    def convert_dict(data: List[Dict[str, Any]]) -> Dict[str, List]:
        table: Dict[str, List] = {
            "排名": [],
            "公会名": [],
            "分数": [],
            "上期排名": [],
            "会长": [],
            "会长ID": [],
        }
        for i in data:
            table["排名"].append(i["rank"])
            table["公会名"].append(i["clanName"])
            table["分数"].append(i["damage"])
            table["上期排名"].append(i["gradeRank"])
            table["会长"].append(i["userName"])
            table["会长ID"].append(i["leaderViewerId"])
        return table

    async def draw(self, table: List[Dict[str, Any]]) -> bytes:
        data: Dict[str, List] = self.convert_dict(table)
        length = len(data[list(data.keys())[0]])
        image = Image.new("RGBA", (944, 60 * (length + 1)), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        # ------------------------ 每行画一条浅浅的灰色的线 ------------------------

        for i in range(1, length):
            draw.line((0, 60 * i, 944, 60 * i), fill=(240, 240, 240), width=1)

        for i in range(1, len(data.keys()) + 1):
            draw.line(
                (self.slit[i - 1], 10, self.slit[i - 1], 50),
                fill=(240, 240, 240),
                width=1,
            )

        # ------------------------ 遍历每个数据画表格 ------------------------
        def get_centre(key: str, size: int) -> Tuple[float, float]:
            font_box = ImageFont.truetype(self.font, size).getbbox(key)
            font_width = font_box[2] - font_box[0]
            font_height = font_box[3] - font_box[1]
            return (font_width / 2, font_height / 2)

        for count, (key, value) in enumerate(data.items()):
            font_center = get_centre(key, 20)
            font_left_top = (
                self.slit[count]
                + (self.slit[count + 1] - self.slit[count]) / 2
                - font_center[0],
                30 - font_center[1],
            )
            draw.text(
                font_left_top, key, fill="black", font=ImageFont.truetype(self.font, 20)
            )
            for i in range(len(value)):
                font_center = get_centre(str(value[i]), 20)
                font_left_top = (
                    self.slit[count]
                    + (self.slit[count + 1] - self.slit[count]) / 2
                    - font_center[0],
                    60 * (i + 1) + 30 - font_center[1],
                )
                draw.text(
                    font_left_top,
                    str(value[i]),
                    fill="black",
                    font=ImageFont.truetype(self.font, 20),
                )
        image_bytes = BytesIO()
        image.save(image_bytes, format="png")
        return image_bytes.getvalue()


drawtable = DrawTable()

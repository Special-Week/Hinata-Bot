import os
from base64 import b64encode
from io import BytesIO
from sys import exc_info
from traceback import format_exc
from typing import Tuple, Union

from nonebot.log import logger
from PIL import Image, ImageDraw, ImageFont

dir = os.path.dirname(os.path.abspath(__file__))
fontPath = f"{dir}{os.sep}color.ttf"


def rgb2hex(rgb: Tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def hex2rgb(hex: str) -> Tuple[int, int, int]:
    hex = hex[1:] if hex[0] == "#" else hex
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


# 相反色 Hex 值生成
def compColorHex(rgb: Tuple[int, int, int]) -> str:
    compRgb = tuple(255 - i for i in rgb)
    return rgb2hex(compRgb)


# Pillow 绘制字体设置
def font(size: int):
    return ImageFont.truetype(font=fontPath, size=size)


# 图片转换为 Base64 编码
def img2Base64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG", quality=100)
    base64_str = b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str


# 色图生成！
async def gnrtImg(color: Union[str, Tuple]) -> str:
    try:
        if isinstance(color, str):
            cHex, cRGB = color.upper(), hex2rgb(color)
        else:
            color = tuple(int(i) for i in color)
            cHex, cRGB = rgb2hex(color), color
        txtColor = compColorHex(cRGB)
        img = Image.new("RGB", (200, 200), cRGB)
        draw = ImageDraw.Draw(img)
        # 居中绘制 Hex 值
        hexCenter = font(32).getsize(cHex)
        draw.text(
            (int((200 - hexCenter[0]) / 2), 60),
            cHex, font=font(32), fill=txtColor
        )
        # 居中绘制 RGB 值
        rgbTxt = f"rgb({', '.join([str(i) for i in cRGB])})"
        rgbCenter = font(16).getsize(rgbTxt)
        draw.text(
            (int((200 - rgbCenter[0]) / 2), 200 - 60 - rgbCenter[1]),
            rgbTxt, font=font(16), fill=txtColor
        )
        return img2Base64(img)
    except Exception:
        logger.warning(format_exc())
        return "不许色色！\n" + str(exc_info()[0])

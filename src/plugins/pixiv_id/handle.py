import random
from io import BytesIO

from httpx import AsyncClient
from loguru import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from PIL import Image


class PixivID:
    def __init__(self) -> None:
        self.url = "https://pixiv.re/"


    async def main(
        self,
        matcher: Matcher,
        msg: Message = CommandArg()
    ):
        _id = msg.extract_plain_text().strip()
        url = f"{self.url}{_id}.jpg"
        # 下载图片
        try:
            content = await self.down_pic(url)
        except Exception:
            await matcher.finish("图片下载失败")
        # 返回值为404则没有这个id或者id为多图模式
        if type(content) == int:
            await matcher.finish("没有找到这个id,多张作品请用xxxxxx-x格式")
        # 打开图像,随机修改左上角第一颗像素点,并且转为base64编码
        image = Image.open(BytesIO(content))
        img_format = image.format  # 获取图片的格式
        image.load()[0, 0] = (random.randint(0, 255),
                            random.randint(0, 255), random.randint(0, 255))
        byte_data = BytesIO()
        image.save(byte_data, format=img_format, quality=95)
        pic = byte_data.getvalue()

        # 发送图片
        try:
            await matcher.send(MessageSegment.image(pic))
        except Exception:
            await matcher.send(f"消息被风控,图片发送失败,这是连接{url}")



    # 下载图片并且返回content,或者status_code
    async def down_pic(self, url: str):
        async with AsyncClient() as client:
            try:
                re = await client.get(url=url, timeout=120)
                if re.status_code == 200:
                    logger.success("插件pixiv_id成功获取图片")
                    return re.content
                else:
                    logger.error(f"插件pixiv_id获取图片失败: {re.status_code}")
                    return re.status_code
            except Exception:
                logger.error("http访问超时")
                return 408
            
            
pixiv_id = PixivID()

from httpx import AsyncClient
from nonebot import logger
from nonebot.log import logger
import random
import sqlite3
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
error = "Error:"
conn = sqlite3.connect(
    Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db")
cur = conn.cursor()


async def get_setu(keyword="", r18=False) -> list:
    # 根据keyword和r18进行查询拿到数据
    cursor = cur.execute(
        f"SELECT * from main where tags like \'%{keyword}%\'  and r18=\'{r18}\'")
    db_data = cursor.fetchall()
    if db_data == []:
        return [error, f"图库中没有搜到关于{keyword}的图。", False]
    setu_data = random.choice(db_data)
    setu_title = setu_data[3]
    setu_url = setu_data[11].replace('i.pixiv.cat', 'i.pixiv.re')
    setu_pid = setu_data[0]
    setu_author = setu_data[4]

    data = (
        "标题:"
        + setu_title
        + "\npid:"
        + str(setu_pid)
        + "\n画师:"
        + setu_author
    )
    logger.info("\n"+data+"\ntags:"+setu_data[8])

    content = await down_pic(setu_url)
    if type(content) == int:
        return [error, f"图片下载失败", False]

    # 随机修改左上角第一颗像素的颜色
    image = Image.open(BytesIO(content))
    image.load()[0, 0] = (random.randint(0, 255),
                          random.randint(0, 255), random.randint(0, 255))
    byte_data = BytesIO()
    image.save(byte_data, format="PNG")
    # pic的图片的base64编码
    pic = byte_data.getvalue()

    return [pic, data, True, setu_url]


# 下载图片并且返回content,或者status_code
async def down_pic(url):
    async with AsyncClient() as client:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return re.status_code

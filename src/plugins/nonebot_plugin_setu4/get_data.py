import asyncio
import os
import random
import sqlite3
from io import BytesIO
from pathlib import Path

from httpx import AsyncClient
from nonebot.log import logger
from PIL import Image

from .config import config
from .utils import utils


class GetSetu:
    def __init__(self) -> None:
        self.error = "Error:"
        # 数据库相关
        database_path = Path(__file__).parent / "resource"
        self.conn = sqlite3.connect(database_path / "lolicon.db")
        self.cur = self.conn.cursor()
        # 色图路径以及本地图片文件
        self.setu_save = config.setu_save
        self.all_file_name = os.listdir(self.setu_save) if config.setu_save else []

    # 返回列表,内容为setu消息(列表套娃)
    async def get_setu(
        self, 
        num: int = 1, 
        quality: int = 75, 
        r18: bool = False, 
        keywords: list = None
    ) -> list:
        if keywords is None:
            keywords = []
        data = []
        # sql操作,根据keyword和r18进行查询拿到数据, sql操作要避免选中status为unavailable的
        if not keywords:   
            sql = f"SELECT pid,title,author,r18,tags,urls from main where r18='{r18}' and status!='unavailable' order by random() limit {num}"
        elif len(keywords) == 1:
            sql = f"SELECT pid,title,author,r18,tags,urls from main where (tags like '%{keywords[0]}%' or title like '%{keywords[0]}%' or author like '%{keywords[0]}%') and r18='{r18}' and status!='unavailable' order by random() limit {num}"
        else:               # 多tag的情况下的sql语句
            tag_sql = "".join(
                f"tags like '%{i}%'"
                if i == keywords[-1]
                else f"tags like '%{i}%' and "
                for i in keywords
            )
            sql = f"SELECT pid,title,author,r18,tags,urls from main where (({tag_sql}) and r18='{r18}' and status!='unavailable') order by random() limit {num}"
        cursor = self.cur.execute(sql)
        db_data = cursor.fetchall()

        # 如果没有返回结果
        if db_data == []:
            data.append([self.error, f"图库中没有搜到关于{keywords}的图。", False])
            return data

        async with AsyncClient() as client:
            tasks = [self.pic(setu, quality, client) for setu in db_data]
            data = await asyncio.gather(*tasks)
        return data



    async def pic(
        self,
        setu: list, 
        quality: int, 
        client: AsyncClient
    ) -> list:
        """返回setu消息列表,内容 [图片, 信息, True/False, url]"""
        setu_proxy = utils.read_proxy()            # 读取代理
        setu_pid = setu[0]                   # pid
        setu_title = setu[1]                 # 标题
        setu_author = setu[2]                # 作者
        setu_r18 = setu[3]                   # r18
        setu_tags = setu[4]                  # 标签
        setu_url = setu[5].replace('i.pixiv.re', setu_proxy)     # 图片url

        data = (
            "标题:"
            + setu_title
            + "\npid:"
            + str(setu_pid)
            + "\n画师:"
            + setu_author
        )

        logger.info("\n"+data+"\ntags:" +
                    setu_tags+"\nR18:"+setu_r18)
        file_name = setu_url.split("/")[-1]

        # 判断文件是否本地存在
        is_in_all_file_name = file_name in self.all_file_name
        if is_in_all_file_name:
            logger.info("图片本地存在")
            image = Image.open(f"{self.setu_save}/{file_name}")
        else:
            logger.info(f"图片本地不存在,正在去{setu_proxy}下载")
            content = await self.down_pic(setu_url, client)
            if type(content) == int:
                return [self.error, f"图片下载失败, 状态码{content}", False, setu_url]
            # 尝试打开图片, 如果失败就返回错误信息
            try:
                image = Image.open(BytesIO(content))
            except Exception as e:
                return [self.error, f"图片下载失败, 错误信息:{e}", False, setu_url]
            # 保存图片, 如果save_path不为空, 以及图片不在all_file_name中, 那么就保存图片
            if self.setu_save:
                try:
                    with open(f"{self.setu_save}/{file_name}", "wb") as f:
                        f.write(content)
                    self.all_file_name.append(file_name)
                except Exception as e:
                    logger.error(f'图片存储失败: {e}')
        try:
            pic = await self.change_pixel(image, quality)
        except Exception as e:
            logger.error("图片处理失败")
            return [self.error, f"图片处理失败: {e}", False, setu_url]
        return [pic, data, True, setu_url]



    async def change_pixel(
        self,
        image: Image, 
        quality: int
    ) -> bytes:
        """图片左右镜像,并且随机修改第一个像素点"""
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image = image.convert("RGB")
        image.load()[0, 0] = (random.randint(0, 255),
                            random.randint(0, 255), random.randint(0, 255))
        byte_data = BytesIO()
        image.save(byte_data, format="JPEG", quality=quality)
        return byte_data.getvalue()

    async def down_pic(
        self,
        url: str, 
        client: AsyncClient
    ):
        """下载图片并且返回content(bytes),或者status_code(int)"""
        try:
            re = await client.get(url=url, timeout=120)
            if re.status_code != 200:
                if re.status_code == 404:
                    await self.update_status_unavailable(url.replace(utils.read_proxy(), 'i.pixiv.re'))
                return re.status_code
            logger.success("成功获取图片")
            return re.content
        except Exception:
            return 408
        
    
    async def update_status_unavailable(self, urls: str) -> None:
        """更新数据库中的图片状态为unavailable"""
        # 手搓sql语句
        sql = f"UPDATE main set status='unavailable' where urls='{urls}'"
        self.cur.execute(sql)  # 执行
        self.conn.commit()                   # 提交事务


get_setu = GetSetu()
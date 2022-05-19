from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import MessageSegment, Message
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw
import os
from io import BytesIO

def is_number(s: str) -> bool:
    """
    说明：
        检测 s 是否为数字
    参数：
        :param s: 文本
    """
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata

        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


url = "http://www.eclzz.mobi"



def get_download_link(_url: str) -> str:
    """
    获取资源下载地址
    :param _url: 链接
    """
    text = requests.get(f"{url}{_url}").text
    soup = BeautifulSoup(text, "lxml")
    return soup.find("a", {"id": "down-url"})["href"]


def get_bt_info(keyword: str, page: int):
    """
    获取资源信息
    :param keyword: 关键词
    :param page: 页数
    """
    text = requests.get(f"{url}/s/{keyword}_rel_{page}.html", timeout=5).text
    if text.find("大约0条结果") != -1:
        return
    soup = BeautifulSoup(text, "lxml")
    item_lst = soup.find_all("div", {"class": "search-item"})
    bt_max_num=1
    for item in item_lst[:bt_max_num]:
        divs = item.find_all("div")
        title = (
            str(divs[0].find("a").text)
            .replace("<em>", "")
            .replace("</em>", "")
            .strip()
        )
        spans = divs[2].find_all("span")
        type_ = spans[0].text
        create_time = spans[1].find("b").text
        file_size = spans[2].find("b").text
        link = get_download_link(divs[0].find("a")["href"])
        yield title, type_, create_time, file_size, link



bt = on_command("磁力搜索", priority=5, block=True)

@bt.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if msg:
        keyword = None
        page = 1
        if n := len(msg):
            keyword = msg[0]
        if n > 1 and is_number(msg[1]) and int(msg[1]) > 0:
            page = int(msg[1])
        state["keyword"] = keyword
        state["page"] = page
    else:
        state["page"] = 1




@bt.got("keyword", prompt="请输入要查询的内容！")
async def _(
    keyword: str = ArgStr("keyword"),
    page: str = ArgStr("page"),
):
    try:
        message=""
        list1 = get_bt_info(keyword, page)
        for i in list1:
            message+="标题：{title}\n类型：{type}\n创建时间：{create_time}\n文件大小：{file_size}\n".format(title = i[0],type=i[1],create_time=i[2],file_size=i[3])
            link=i[4]
        im = Image.new("RGB", (500, 150), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        font = ImageFont.truetype(os.path.join("fonts", "华康方圆体W7.TTC"), 32)
        dr.text((10, 5), message, font=font, fill="#000000")
        new_img = im.convert("RGB")
        img_byte = BytesIO()
        new_img.save(img_byte, format='PNG')
        binary_content = img_byte.getvalue()
        await bt.send(MessageSegment.image(binary_content)+f"链接:{link}")
    except TimeoutError:
        await bt.finish(f"搜索 {keyword} 超时...")
    except Exception as e:
        await bt.finish(f"{keyword} 未搜索到... 或者遇其他未知错误..")
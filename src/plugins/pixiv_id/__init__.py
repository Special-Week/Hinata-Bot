import requests
from PIL import Image
from io import BytesIO
import random
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot
from nonebot import on_command
from nonebot.params import CommandArg
import asyncio
pixiv_id = on_command("pixiv_id", block=True)


@pixiv_id.handle()
async def _(bot: Bot, msg: Message = CommandArg()):
    # 获取消息文本
    id = msg.extract_plain_text()
    url = f"https://pixiv.re/{id}.jpg"
    # 下载图片
    try:
        content = down_pic(url)
    except:
        await pixiv_id.finish("图片下载失败")
    # 返回值为404则没有这个id或者id为多图模式
    if content == 404:
        await pixiv_id.finish("没有找到这个id,多张作品请用xxxxxx-x格式")
    # 打开图像,随机修改左上角第一颗像素点,并且转为base64编码
    image = Image.open(BytesIO(content))
    image.load()[0, 0] = (random.randint(0, 255),
                          random.randint(0, 255), random.randint(0, 255))
    byte_data = BytesIO()
    image.save(byte_data, format="PNG")
    pic = byte_data.getvalue()
    # 发送图片
    try:
        msg_id = await pixiv_id.send(MessageSegment.image(pic))
        msg_id = msg_id['message_id']
        await asyncio.sleep(100)
        try:
            await bot.delete_msg(message_id=msg_id)
        except:
            pass
        return

    except:
        await pixiv_id.finish(f"消息被风控,图片发送失败,这是连接{url}")


# 下载图片
def down_pic(url):
    headers = {
        "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    re = requests.get(url=url, headers=headers, timeout=120)
    if re.status_code == 200:
        return re.content
    else:
        return re.status_code

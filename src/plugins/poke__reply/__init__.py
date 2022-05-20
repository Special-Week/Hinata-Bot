
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import PokeNotifyEvent,Message,Bot
import random
random.seed(1)
import asyncio
import base64
from httpx import AsyncClient
from nonebot import logger
from nonebot.log import logger
from re import findall

poke_ = on_notice(priority=5, block=False)
poke__reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    "你戳你🐎呢？！",
    "请不要戳Hinata >_<",
    "放手啦，不给戳QAQ",
    "喂(#`O′) 戳Hinata干嘛！",
    "戳坏了，赔钱！",
    "戳坏了",
    "嗯……不可以……啦……不要乱戳",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "有事恁叫我，别天天一个劲戳戳戳！",
    "欸很烦欸！你戳🔨呢",
    "再戳一下试试？",
    "正在关闭对您的所有服务...关闭成功",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
    "正在定位您的真实地址...定位成功。轰炸机已起飞",
]


@poke_.handle()
async def _poke_event(bot: Bot,event: PokeNotifyEvent)-> bool:
    if event.is_tome():
        if(random.random() < 0.35):
            pic = await get_setu()
            message=f"别戳了别戳了,这张setu给你了,让我安静一会儿,一分钟后我要撤回\n"+Message(pic[1])+Message(pic[0])
            setu_msg_id = await poke_.send(message)
            setu_msg_id = setu_msg_id['message_id']
            await asyncio.sleep(60)
            await bot.delete_msg(message_id=setu_msg_id)
            return
        await poke_.send(message=f"{random.choice(poke__reply)}")

async def get_setu() -> list:
    async with AsyncClient() as client:
        req_url = "https://api.lolicon.app/setu/v2"
        params = {
            "r18": 0,
            "size": "regular",
            "proxy": "i.pixiv.re",
        }
        res = await client.get(req_url, params=params, timeout=120)
        logger.info(res.json())
        setu_title = res.json()["data"][0]["title"]
        setu_url = res.json()["data"][0]["urls"]["regular"]
        content = await down_pic(setu_url)
        setu_pid = res.json()["data"][0]["pid"]
        setu_author = res.json()["data"][0]["author"]
        base64 = convert_b64(content)
        if type(base64) == str:
            pic = "[CQ:image,file=base64://" + base64 + "]"
            data = (
                "标题:"
                + setu_title
                + "\npid:"
                + str(setu_pid)
                + "\n画师:"
                + setu_author
            )
        return [pic, data, setu_url]

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

def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic

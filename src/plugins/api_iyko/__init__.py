from nonebot import on_command,on_regex
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import MessageSegment
import requests
import asyncio


xh = on_command("来点笑话", priority=5, block=True)
@xh.handle()
async def _():
    try:
        url_xh = "https://api.iyk0.com/xh"
        resp = requests.get(url_xh).text
        arr=resp.split('\\n')
        await xh.send(message=arr)
    except Exception as e:
        await xh.send("你给我讲个笑话")



chp = on_command("来点彩虹屁",priority=5,block=True)
@chp.handle()
async def _():
    try:
        url_chp = "https://api.iyk0.com/chp"
        resp = requests.get(url_chp)
        res=resp.json()
        txt=res['txt']
        await chp.send(message=f"{txt}")
    except Exception as e:
        await chp.send("你给我放个屁")




wzrjcsdrz = on_command("我在人间", priority=5, block=True)
@wzrjcsdrz.handle()
async def _():
    try:
        url_renjian = "https://api.iyk0.com/renjian"
        resp = requests.get(url_renjian).text
        await wzrjcsdrz.send(message=resp)
    except Exception as e:
        await wzrjcsdrz.send("出错了，我先爬爬爬")


twqh = on_command("来点土味情话", priority=5, block=True)
@twqh.handle()
async def _():
    try:
        url_twqh = "https://api.iyk0.com/twqh"
        resp = requests.get(url_twqh).text
        await twqh.send(message=resp)
    except Exception as e:
        await twqh.send("出错了，我先爬爬爬")


tgrj=on_command("来点逆天",priority=5, block=True)
@tgrj.handle()
async def _():
    try:
        url_tgrj="https://api.iyk0.com/tiangou"
        resp = requests.get(url_tgrj).text
        await tgrj.send(message=resp)
    except Exception as e:
        await tgrj.send("出错了，我先爬爬爬")



sgyl=on_command("来点伤感语录",priority=5, block=True)
@sgyl.handle()
async def _():
    try:
        url_sgyl="https://api.iyk0.com/sg"
        resp = requests.get(url_sgyl).text
        await sgyl.send(message=resp)
    except Exception as e:
        await sgyl.send("出错了，我先爬爬爬")



readworld=on_command("60秒读世界",aliases={"读世界"},priority=10,block=True)
@readworld.handle()
async def _():
    try:
        url='https://api.iyk0.com/60s'
        resp = requests.get(url).json()["imageUrl"]
        await readworld.send(MessageSegment.image(resp))
    except:
        await readworld.send("ERROR:API异常")


today = on_command("今天节日",priority=10,block=True)
@today.handle()
async def _():
    try:
        resp = requests.get('https://api.iyk0.com/jr/').json()
        await today.send(resp["today"] + "\n" + resp["surplus"])
    except:
        await today.send("ERROR:API异常")



rain = on_command("降雨预报",priority=10,block=True)
@rain.handle()
async def _():
    try:
        await rain.send(MessageSegment.image(requests.get('https://api.iyk0.com/jyu').json()["img"]))
    except:
        await rain.send("ERROR:API异常")



coser = on_regex("^(cos|COS|coser|括丝)$", priority=5, block=True)
@coser.handle()
async def _(bot: Bot):
    url = "https://api.iyk0.com/cos"
    try:
        msg_id = await coser.send(MessageSegment.image(url))
        msg_id = msg_id['message_id']
         # 自动撤回
        await asyncio.sleep(100)
        await bot.delete_msg(message_id=msg_id)
    except:
        await coser.send("出错了!你来给大家整点")

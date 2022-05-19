from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment

yydz = on_command('一眼丁真',aliases={'yydz'}, priority=10,block=True)


@yydz.handle()
async def _yiyandingzhen():
    url = 'https://api.aya1.top/randomdj'
    try:
        await yydz.send(MessageSegment.image(url))
    except:
        await yydz.send("ERROR:API异常")

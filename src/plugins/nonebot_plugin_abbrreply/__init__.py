from httpx import AsyncClient
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message


async def get_sx(word):
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"

    data = {
        "text": f"{word}"
    }
    async with AsyncClient() as client:
        res = await client.post(url=url, json=data)
        res = res.json()
    return res if res else []

sx = on_command('sx',aliases={"缩写"}, block=True,priority=10)


@sx.handle()
async def _(msg: Message = CommandArg()):
    msg = msg.extract_plain_text()
    data = await get_sx(msg)
    result = ""
    try:
        data = data[0]
        name = data['name']
        try:
            content = data['trans']
            result += ' , '.join(content)
        except KeyError:
            pass
        try:
            inputs = data['inputting']
            result += ' , '.join(inputs)
        except KeyError:
            pass
        if result:
            await sx.finish(message=name + "可能解释为：\n" + result)
        await sx.finish(message=f"没有找到缩写 {msg} 的可能释义")
    except KeyError:
        await sx.finish(message=f"出错啦")


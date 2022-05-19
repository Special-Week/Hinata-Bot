from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape



wettr = on_command('天气', aliases={'wttr', 'weather', 'tianqi'})


@wettr.handle()
async def _handle(matcher: Matcher, city: Message = CommandArg()):
    if city.extract_plain_text() and city.extract_plain_text()[0]!='_':
        matcher.set_arg('city', city)


@wettr.got('city', prompt='你想查询哪个城市的天气呢？')
async def _(city: str = ArgPlainText('city')):
    if city[0]!='_':
        await wettr.send('少女观星中...', at_sender=True)
        await wettr.send(MessageSegment.image(file=f'http://zh.wttr.in/{escape(city)}.png', cache=False), at_sender=True)
    else:
        await wettr.reject_arg('city',prompt='不能使用“_”作为查询前缀！请重新输入！')

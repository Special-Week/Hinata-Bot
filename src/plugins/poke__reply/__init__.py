from nonebot import on_notice
from nonebot.adapters.onebot.v11 import PokeNotifyEvent,Bot
import random
NICKNAME: str = "Hinata"
poke_ = on_notice(priority=5, block=False)
poke__reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    "你戳你🐎呢？！",
    f"请不要戳{NICKNAME} >_<",
    "放手啦，不给戳QAQ",
    f"喂(#`O′) 戳{NICKNAME}干嘛！",
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
        await poke_.send(message=f"{random.choice(poke__reply)}")

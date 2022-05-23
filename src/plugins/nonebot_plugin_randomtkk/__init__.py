from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from nonebot.params import Depends, CommandArg, State
from nonebot.rule import Rule
from .handler import random_tkk_handler

__randomtkk_vsrsion__ = "v0.1.1"
__randomtkk_notes__ = f'''
随机唐可可 {__randomtkk_vsrsion__}
[随机唐可可]+[简单/普通/困难/地狱/自定义数量] 开启唐可可挑战
不指定难度默认普通模式
可替换为[随机鲤鱼/鲤鱼王/Liyuu/liyuu]
答案格式：[答案是][行][空格][列]，例如：答案是114 514
[找不到唐可可/唐可可人呢/呼叫鲤鱼姐] 发起者可提前结束游戏
'''.strip()

def inplaying_check(event: MessageEvent) -> bool:
    if isinstance(event, GroupMessageEvent):
        uuid = str(event.group_id)
    else:
        uuid = str(event.user_id)
        
    return random_tkk_handler.check_tkk_playing(uuid)

def starter_check(event: MessageEvent) -> bool:
    uid = str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
    else:
        gid = None
        
    return random_tkk_handler.check_starter(gid, uid)

random_tkk = on_command(cmd="随机唐可可", aliases={"随机鲤鱼", "随机鲤鱼王", "随机Liyuu", "随机liyuu"}, priority=12)
guess_tkk = on_command(cmd="答案是", rule=Rule(inplaying_check), priority=12, block=True)
surrender_tkk = on_command(cmd="找不到唐可可", aliases={"唐可可人呢", "呼叫鲤鱼姐"}, rule=Rule(starter_check), priority=12, block=True)
 
@random_tkk.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    uid = str(event.user_id)
    
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        if random_tkk_handler.check_tkk_playing(gid):
            await matcher.finish("游戏已经开始啦！", at_sender=True)
    else:
        if random_tkk_handler.check_tkk_playing(uid):
            await matcher.finish("游戏已经开始啦！")
        
    args = args.extract_plain_text().strip().split()

    if not args:
        await matcher.send("未指定难度，默认普通模式")
        level = "普通"
    elif args and len(args) == 1: 
        if args[0] == "帮助":
            await matcher.finish(__randomtkk_notes__)
        level = args[0]
    else:
        await matcher.finish("参数太多啦~")
    
    if isinstance(event, GroupMessageEvent):
        img_file, waiting = await random_tkk_handler.one_go(matcher, gid, uid, level)
    else:
        img_file, waiting = await random_tkk_handler.one_go(matcher, uid, uid, level)
    
    await matcher.send(MessageSegment.image(img_file))
    
    # 确保在此为send，超时回调内还需matcher.finish
    await matcher.send(f"将在 {waiting}s 后公布答案\n答案格式：[答案是][行][空格][列]\n例如：答案是114 514\n提前结束游戏请发起者输入[找不到唐可可/唐可可人呢]")

async def get_user_guess(args: Message = CommandArg(), state: T_State = State()):
    args = args.extract_plain_text().strip().split()

    if not args:
        await guess_tkk.finish("答案是啥捏？")
    elif args and len(args) == 1:    
        await guess_tkk.finish("答案格式错误~")
    elif args and len(args) == 2:
        args = [int(x) for x in args]   # 类型转换str -> int
        return {**state, "guess": args}
    else:
        await guess_tkk.finish("参数太多啦~")

@guess_tkk.handle()
async def _(event: MessageEvent, state: T_State = Depends(get_user_guess)): 
    uid = str(event.user_id)
    pos = state["guess"]

    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        if random_tkk_handler.check_answer(gid, pos):
            if not random_tkk_handler.binggo_close_game(gid):
                await guess_tkk.finish("结束游戏出错……")
            await guess_tkk.finish("答对啦，好厉害！", at_sender=True)
        else:
            await guess_tkk.finish("不对哦~", at_sender=True)
    else:
        if random_tkk_handler.check_answer(uid, pos):
            if not random_tkk_handler.binggo_close_game(uid):
                await guess_tkk.finish("结束游戏出错……")
            await guess_tkk.finish("答对啦，好厉害！")
        else:
            await guess_tkk.finish("不对哦~")
        
@surrender_tkk.handle()
async def _(matcher: Matcher, event: MessageEvent):
    uid = str(event.user_id)
    
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        await random_tkk_handler.surrender(matcher, gid)
    else:
        await random_tkk_handler.surrender(matcher, uid)

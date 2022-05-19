import re
from typing import List, Union
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText, State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot_plugin_htmlrender import text_to_pic

from .data_source import CaiyunAi, model_list


__help__plugin_name__ = 'caiyunai'
__des__ = '彩云小梦AI续写'
__cmd__ = '''
@我 续写/彩云小梦 {text}
'''.strip()
__short_cmd__ = '@我 续写 xxx'
__example__ = '''
@小Q 续写 小Q是什么
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


novel = on_command('续写', aliases={'彩云小梦'},
                   block=True, rule=to_me(), priority=11)


@novel.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    if content:
        matcher.set_arg('content', msg)


@novel.got('content', prompt='请发送要续写的内容')
async def _(matcher: Matcher, content: str = ArgPlainText(), state: T_State = State()):
    matcher.set_arg('reply', Message(f'续写{content}'))
    caiyunai = CaiyunAi()
    state['caiyunai'] = caiyunai


@novel.got('reply')
async def _(bot: Bot, event: GroupMessageEvent,
            state: T_State = State(), reply: str = ArgPlainText()):
    caiyunai: CaiyunAi = state.get('caiyunai')

    match_continue = re.match(r'续写\s*(\S+.*)', reply, re.S)
    match_select = re.match(r'选择分支\s*(\d+)', reply)
    match_model = re.match(r'切换模型\s*(\S+)', reply)

    if match_model:
        model = match_model.group(1).strip()
        if model not in model_list:
            model_help = f"支持的模型：{'、'.join(list(model_list))}\n发送“切换模型 名称”切换模型"
            await novel.reject(model_help)
        else:
            caiyunai.model = model
            await novel.reject(f'模型已切换为：{model}')
    elif match_continue:
        content = match_continue.group(1)
        caiyunai.content = content
    elif match_select:
        num = int(match_select.group(1))
        if num < 1 or num > len(caiyunai.contents):
            await novel.reject('请发送正确的编号')
        caiyunai.select(num - 1)
    else:
        await novel.finish('续写已结束')

    await novel.send('loading...')
    err_msg = await caiyunai.next()
    if err_msg:
        await novel.finish(f"出错了：{err_msg}")

    msgs = []
    nickname = model_list[caiyunai.model]['name']
    help_msg = '发送“选择分支 编号”选择分支\n发送“续写 内容”手动添加内容\n发送“切换模型 名称”切换模型'
    msgs.append(help_msg)
    result = await text_to_pic(caiyunai.result)
    msgs.append(MessageSegment.image(result))
    for i, content in enumerate(caiyunai.contents, start=1):
        msgs.append(f'{i}、\n{content}')
    try:
        await send_forward_msg(bot, event, nickname, bot.self_id, msgs)
    except:
        await novel.finish('消息发送失败')
    await novel.reject()


async def send_forward_msg(bot: Bot, event: GroupMessageEvent, name: str, uin: str,
                           msgs: List[Union[str, MessageSegment]]):
    def to_json(msg):
        return {
            'type': 'node',
            'data': {
                'name': name,
                'uin': uin,
                'content': msg
            }
        }
    msgs = [to_json(msg) for msg in msgs]
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)

from asyncio import sleep
import imp
from io import BytesIO
from typing import Dict, List
from httpx import AsyncClient
from nonebot import on_command, on_message, on_shell_command
from nonebot import matcher
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
    MessageSegment,
)
import qrcode
from nonebot.params import Arg, ArgPlainText, CommandArg, ShellCommandArgv, State
from nonebot.rule import ArgumentParser, ParserExit, command
from nonebot.typing import T_State
from PIL import Image
from pyzbar.pyzbar import decode
from nonebot.matcher import Matcher
qr_map: Dict[str, str] = {}


async def check_qrcode(event: MessageEvent, state: T_State = State()) -> bool:
    if isinstance(event, MessageEvent):
        for msg in event.message:
            if msg.type == "image":
                url: str = msg.data["url"]
                state["url"] = url
                return True
        return False


notice_qrcode = on_message(check_qrcode, block=False, priority=90)


@notice_qrcode.handle()
async def handle_pic(event: MessageEvent, state: T_State = State()):
    if isinstance(event, GroupMessageEvent):
        try:
            group_id: str = str(event.group_id)
            qr_map.update({group_id: state["url"]})
        except AttributeError:
            pass
    elif isinstance(event, PrivateMessageEvent):
        try:
            user_id: str = str(event.user_id)
            qr_map.update({user_id: state["url"]})
        except ArithmeticError:
            pass


pqr = on_command("pqr", aliases={"前一二维码", "pqrcode"})


@pqr.handle()
async def handle_pqr(event: MessageEvent):
    try:
        url: str = (
            qr_map[str(event.group_id)]
            if isinstance(event, GroupMessageEvent)
            else qr_map[str(event.user_id)]
        )

        async with AsyncClient() as client:
            res = await client.get(url=url, timeout=10)
        img = Image.open(BytesIO(res.content))
        data = decode(img)
        for i in range(len(data)):
            qr_data = data[i][0]
            await pqr.send(str(qr_data.decode()))
            await sleep(3)
        await pqr.finish()
    except (IndexError):
        await pqr.finish()
    except KeyError:
        await pqr.finish("图不对！")


readqrcode = on_command("qrcode", aliases={"qr", "二维码"})


@readqrcode.handle()
async def handle_first_receive(arg: Message = CommandArg(), state: T_State = State()):
    msg = arg
    if msg:
        state["qr_img"] = msg
    pass


@readqrcode.got("qr_img", prompt="图呢")
async def get_qr_img(state: T_State = State()):
    msg: Message = state["qr_img"]
    # try:
    for msg_sag in msg:
        if msg_sag.type == "image":
            url = msg_sag.data["url"]

            async with AsyncClient() as client:
                res = await client.get(url=url, timeout=10)
            img = Image.open(BytesIO(res.content))
            data = decode(img)
            for i in range(len(data)):
                qr_data = data[i][0]
                await readqrcode.send(str(qr_data.decode()))
                await sleep(3)
            await readqrcode.finish()
        else:
            await readqrcode.finish("这啥？指令已取消")


parser = ArgumentParser("gqr", description="生成二维码")
parser.add_argument("-m", "--mask", help="添加图像遮罩", action="store_true")
parser.add_argument("-e", "--embeded", help="添加中间logo", action="store_true")


makeqrcode = on_command("make_qrcode", aliases={"make_qr", "生成二维码"})

def make_qr(str):
    qr=qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M, 
        box_size=10,
        border=2, 
    )
    qr.add_data(str)
    qr.make(fit=True)
    img=qr.make_image()
    return img

@makeqrcode.handle()
async def _handle_first_receive(matcher: Matcher, target_text: Message = CommandArg()):
    if target_text.extract_plain_text():
         matcher.set_arg('target_text', target_text)

@makeqrcode.got("target_text", prompt="请输入要转化为二维码的文本")
async def _(target_text: str = ArgPlainText('target_text')):
    
    result = make_qr(target_text)
    new_img = result.convert("RGB")
    img_byte = BytesIO()
    new_img.save(img_byte, format='PNG')
    binary_content = img_byte.getvalue()
    await makeqrcode.finish(MessageSegment.image(binary_content))
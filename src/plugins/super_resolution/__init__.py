import asyncio
import io
import json
import time
from io import BytesIO
from pathlib import Path
from typing import List, Union

import imageio
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from httpx import AsyncClient
from loguru import logger
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import Arg, Depends
from nonebot.typing import T_State
from PIL import Image as IMG
from PIL import ImageSequence
from realesrgan import RealESRGANer

# 超分辨率的参数
upsampler = RealESRGANer(
    scale=4,
    model_path=str(Path(__file__).parent.joinpath("RealESRGAN_x4plus_anime_6B.pth")),
    model=RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=6,
        num_grow_ch=32,
        scale=4,
    ),
    tile=100,
    tile_pad=10,
    pre_pad=0,
    half=False,
)


max_size = 3686400  # 分辨率太大内存或者显存吃不消
isRunning = False  # 正在运行时不允许再次运行

# 响应器部分
superResolution = on_command("超分", priority=5, block=True)  # 超分辨率响应器


def parse_image(key: str):
    async def _key_parser(state: T_State, img: Message = Arg(key)):
        if not get_message_img(img):
            await superResolution.finish("格式错误，超分已取消...")
        state[key] = img

    return _key_parser


@superResolution.handle()
async def _(event: MessageEvent, state: T_State):
    if event.reply:
        state["img"] = event.reply.message
    if get_message_img(event.json()):
        state["img"] = event.message



@superResolution.got(
    "img", prompt="请发送需要处理的图片...", parameterless=[Depends(parse_image("img"))]
)
async def _(img: Message = Arg("img")):
    global isRunning
    if isRunning:  # 正在运行时不允许再次运行
        await superResolution.finish("当前有任务正在进行，请稍后再试...")  # 结束
    isRunning = True  # 开始运行
    img_url = get_message_img(img)[0]  # 获取图片url
    await superResolution.send("开始处理图片...")  # 发送消息
    async with AsyncClient() as client:
        try:
            re = await client.get(img_url)  # 尝试下载图片
        except Exception as e:
            isRunning = False  # 结束
            await superResolution.finish(f"下载图片失败...错误信息:{str(e)}")
        if re.status_code == 200:  # 下载成功
            try:
                image = IMG.open(BytesIO(re.content))  # 打开图片
            except Exception as e:
                isRunning = False  # 重置isRunning
                await superResolution.finish(f"图片打开失败...错误信息{str(e)}")
        else:  # 下载失败
            isRunning = False  # 重置isRunning
            await superResolution.finish("图片下载失败...")  # 结束
    is_gif = getattr(image, "is_animated", False)  # 判断是否为gif
    start = time.time()  # 计时开始
    image_size = image.size[0] * image.size[1]  # 计算图片大小
    if image_size > max_size:  # 图片太大
        isRunning = False  # 重置isRunning并且结束响应器
        await superResolution.finish(
            f"图片尺寸过大！请发送1440p以内即像素数小于 2560*1440=3686400的照片！\n此图片尺寸为：{image.size[0]}×{image.size[1]}={image_size}！"
        )
    result = io.BytesIO()  # 创建一个BytesIO对象
    loop = asyncio.get_event_loop()  # 获取事件循环
    if is_gif:  # 如果是gif
        # outputs = []                                        # 创建一个空列表， 给gif用
        # for i in ImageSequence.Iterator(image):
        #     logger.info(f"一共有{image.n_frames}帧, 正在超第{image.tell()}帧")
        #     image_array=np.array(i)
        #     output, _ = await loop.run_in_executor(None, upsampler.enhance, image_array, 2)
        #     outputs.append(output)
        # imageio.mimsave(result, outputs[1:], format='gif', duration=image.info["duration"] / 1000)
        isRunning = False  # 重置isRunning并且结束响应器
        await superResolution.finish("崽种，不准超GIF，给你block了！")
        # 因为gif每一帧都要超分， 而且超分的时候会占用大量内存， 所以我把gif的超分功能给注释了， 你们可以自己打开
    else:  # 如果不是gif
        image_array = np.array(image)  # 转换为numpy数组
        try:
            output, _ = await loop.run_in_executor(
                None, upsampler.enhance, image_array, 2
            )  # 尝试超分
        except Exception as e:  # 超分失败
            isRunning = False  # 重置isRunning并且结束响应器
            await superResolution.finish(f"超分失败...这是抛出的异常：{str(e)}")
        img = IMG.fromarray(output)  # 转换为PIL图片
        img.save(result, format="PNG")  # format: PNG / JPEG
    end = time.time()  # 计时结束
    use_time = round(end - start, 2)  # 计算用时
    isRunning = False  # 重置isRunning
    await superResolution.finish(
        Message(f"超分完成！处理用时：{use_time}s") + MessageSegment.image(result.getvalue())
    )  # 发送消息





def get_message_img(data: Union[str, Message]) -> List[str]:
    img_list = []
    if isinstance(data, str):
        data = json.loads(data)
        img_list.extend(
            msg["data"]["url"] for msg in data["message"] if msg["type"] == "image"
        )
    else:
        img_list.extend(seg.data["url"] for seg in data["image"])
    return img_list

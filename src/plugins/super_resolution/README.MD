# super_resolution
## 利用本地算力的超分辨率工具(二次元图片)
实测2c2g4m(腾讯云首单那款)的轻量级服务器能够正常运行

> 部分~~大量~~代码借鉴~~抄~~于 https://github.com/zhenxun-org/nonebot_plugins_zhenxun_bot/tree/master/super_resolution


重要的依赖:

    torch                    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116    
    (如果想要能调用显卡的cuda, 请好好安装pytorch, 官网https://pytorch.org/,  验证方法见下) 
    realesrgan               pip install realesrgan                      (先安装好torch)
    basicsr                  pip install basicsr
    
验证cuda能否调用, 返回False | True
```python
import torch
print(torch.cuda.is_available()) 
```
 
其他依赖项

    imageio                    pip install imageio
    numpy                      pip install numpy    
    loguru                     pip install loguru      
    PIL                        pip install pillow    
    httpx                      pip install httpx    
    nonebot2                   pip install nonebot2    
    nonebot.adapters.onebot    pip install nonebot-adapter-onebot


我认为你应该有的依赖:

    io    
    time    
    asyncio    
    json    
    pathlib    
    typing
    
    
    
导包部分:
```python
import io
import time
import json
import asyncio
import imageio
import numpy as np
from io import BytesIO
from pathlib import Path
from loguru import logger
from PIL import Image as IMG
from PIL import ImageSequence
from httpx import AsyncClient
from typing import Union, List
from nonebot import on_command
from nonebot.typing import T_State
from realesrgan import RealESRGANer
from nonebot.params import Arg, Depends
from nonebot.permission import SUPERUSER
from basicsr.archs.rrdbnet_arch import RRDBNet
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
```
    
### 注:
之前在python3.10.4的时候, 安装realesrgan还是basicsr的时候报错了, 当时没仔细研究, 不清楚对3.10.x的兼容性
可以确认的是3.9.x以及3.8.x的python安装还挺顺利的



> 注释已补全, 详细运行逻辑请看注释

> 还有一件事, 因为GIF是一帧一帧处理的大一点的gif可能要处理很久, 所以我把gif部分注释了, 想用可以手动解除那一部分的注释, 并且把紧跟着的finish注释掉

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
import psutil
from PIL import Image, ImageFont, ImageDraw
import os
from io import BytesIO

command = on_command(
    "服务器状态",
    priority=10,
    block=True,
)

@command.handle()
async def server_status():
    data = psutil.virtual_memory()
    obj_Disk = psutil.disk_usage('/')
    the_message = ("硬盘总空间:    "+str(round(obj_Disk.total / (1024.0 ** 3), 2))+"GB")+"\n"+("硬盘已使用:    "+str(round(obj_Disk.used / (1024.0 ** 3), 2))+"GB")+"\n"+("硬盘剩余:      "+str(round(obj_Disk.free / (1024.0 ** 3), 2))+"GB")+"\n"+("硬盘占用率:    "+str(round(obj_Disk.percent, 2))+"%")+ \
        "\n"+("物理核心:      "+str(psutil.cpu_count(logical=False)))+"\n"+('CPU占用率:     ' + str(psutil.cpu_percent(interval=1))+'%')+"\n"+("总内存:        " + str(round(int(data.total) / 1024 / 1024 / 1024, 2))+"GB") + \
        "\n"+("可用内存：     " + str(round(int(data.available) / 1024 / 1024 / 1024, 2)
                            )+"GB")+"\n"+("内存占用率:    %d" % (int(round(data.percent))) + "%")
    im = Image.new("RGB", (950, 340), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(os.path.join("fonts", "simfang.ttf"), 32)
    dr.text((10, 5), the_message, font=font, fill="#000000")
    new_img = im.convert("RGB")
    img_byte = BytesIO()
    new_img.save(img_byte, format='PNG')
    binary_content = img_byte.getvalue()
    await command.finish(MessageSegment.image(binary_content))

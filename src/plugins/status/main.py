import asyncio
import contextlib
import datetime
import os
import platform
import random
import time
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cpuinfo
import psutil
from httpx import AsyncClient
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class Status:
    def __init__(self) -> None:
        self.module_path: Path = Path(__file__).parent
        imgs: List[str] = os.listdir(self.module_path / "img")
        self.imgs: List[Path] = [self.module_path / "img" / img for img in imgs]
        self.start_time: float = time.time()
        self.receive_msg: Dict[int, int] = {}
        self.send_msg: Dict[int, int] = {}
        self.font = "微软正黑体.ttf"

    async def draw_img(self, bot_id: int, nickname: str) -> bytes:
        """绘制图片, 需要传入bot的id和nickname, 返回值为图片的bytes"""

        # ----------------------------------- 加载图片 -----------------------------------

        template = random.choice(self.imgs)
        img = Image.open(template)
        img = img.resize((800, 1364))

        # ----------------------------------- 画矩形 -----------------------------------

        image_new = Image.new("RGBA", (800, 1364), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image_new)
        draw.rectangle((45, 45, 755, 300), fill=(255, 255, 255, 180))
        draw.rectangle((45, 350, 755, 750), fill=(255, 255, 255, 180))
        draw.rectangle((45, 775, 755, 925), fill=(255, 255, 255, 180))
        draw.rectangle((45, 950, 755, 1300), fill=(255, 255, 255, 180))
        image_new = image_new.filter(ImageFilter.GaussianBlur(radius=0.1))
        img.paste(image_new, (0, 0), image_new)

        # ----------------------------------- 贴头像 -----------------------------------

        avatar = await self.get_bot_avatar(bot_id)
        if avatar is None:
            avatar = Image.open(self.module_path / "avatar" / "g.png")
        else:
            avatar = Image.open(BytesIO(avatar))
        avatar = avatar.resize((200, 200))
        bigsize = (avatar.size[0] * 3, avatar.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(avatar.size, Image.LANCZOS)
        avatar.putalpha(mask)
        img.paste(avatar, (72, 72), avatar)

        # ----------------------------------- 基本运行信息 -----------------------------------

        draw = ImageDraw.Draw(img)
        draw.line([(290, 172), (490, 172)], fill=(128, 128, 128), width=3)
        font = ImageFont.truetype(str(self.module_path / "font" / self.font), 48)
        draw.text((290, 110), nickname, font=font, fill=(0, 0, 0))
        # 在横向下面写字
        font = ImageFont.truetype(str(self.module_path / "font" / self.font), 24)
        run_time, program_run_time = await self.get_run_time()
        draw.text((290, 180), f"系统运行时长  {run_time}", font=font, fill=(0, 0, 0))
        draw.text(
            (290, 210), f"Nonebot2运行时长  {program_run_time}", font=font, fill=(0, 0, 0)
        )
        draw.text(
            (290, 240),
            f"接收消息  {self.receive_msg[bot_id]}条    |    发送消息  {self.send_msg[bot_id]}条",
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- CPU信息 -----------------------------------

        (
            cpu_usage,
            cpu_logical_count,
            cpu_count,
            cpu_max_frequency,
            cpu_model,
        ) = await self.get_cpu_status()
        if cpu_usage < 60:
            color = (0, 255, 0)
        elif cpu_usage < 80:
            color = (255, 204, 0)
        else:
            color = (255, 0, 0)

        center = (180, 475)
        outer_radius = 100
        draw.ellipse(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            fill=None,
            outline=(180, 180, 180, 180),
            width=15,
        )
        draw.arc(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            start=-90,
            end=360 * cpu_usage / 100 - 90,
            fill=color,
            width=15,
        )
        text = f"{cpu_usage}%"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] - text_height / 2 - 10),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = "CPU"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = cpu_model
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 35 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"{cpu_count}核{cpu_logical_count}线程"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 61 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"主频{cpu_max_frequency}MHz"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 87 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 内存信息 -----------------------------------

        (
            mem_usage_percent,
            mem_total,
            mem_usage,
            mem_free,
        ) = await self.get_memory_status()
        if mem_usage_percent < 60:
            color = (0, 255, 0)
        elif mem_usage_percent < 80:
            color = (255, 204, 0)
        else:
            color = (255, 0, 0)
        center = (400, 475)
        draw.ellipse(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            fill=None,
            outline=(180, 180, 180, 180),
            width=15,
        )
        draw.arc(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            start=-90,
            end=360 * mem_usage_percent / 100 - 90,
            fill=color,
            width=15,
        )
        text = f"{mem_usage_percent}%"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] - text_height / 2 - 10),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = "RAM"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"总计 {mem_total}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 35 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"已用 {mem_usage}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 61 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"剩余 {mem_free}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 87 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 虚拟内存信息 -----------------------------------

        (
            mem_usage_percent,
            mem_total,
            mem_usage,
            mem_free,
        ) = await self.get_virtual_memory()
        if mem_usage_percent < 60:
            color = (0, 255, 0)
        elif mem_usage_percent < 80:
            color = (255, 204, 0)
        else:
            color = (255, 0, 0)
        center = (620, 475)
        draw.ellipse(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            fill=None,
            outline=(180, 180, 180, 180),
            width=15,
        )
        draw.arc(
            [
                (center[0] - outer_radius, center[1] - outer_radius),
                (center[0] + outer_radius, center[1] + outer_radius),
            ],
            start=-90,
            end=360 * mem_usage_percent / 100 - 90,
            fill=color,
            width=15,
        )
        text = f"{mem_usage_percent}%"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] - text_height / 2 - 10),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = "SWAP"
        font, text_width, text_height = await self.get_font_box(48, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"总计 {mem_total}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 35 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"已用 {mem_usage}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 61 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"剩余 {mem_free}GB"
        font, text_width, text_height = await self.get_font_box(24, text)
        draw.text(
            (center[0] - text_width / 2, center[1] + outer_radius + 87 + text_height),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 磁盘信息 -----------------------------------

        (disk_usage_percent, disk_total, disk_usage) = await self.get_disk_info()
        position = ((185, 790), (720, 840))
        draw.rectangle(position, fill=(180, 180, 180, 180))
        if disk_usage_percent < 60:
            color = (0, 255, 0)
        elif disk_usage_percent < 80:
            color = (255, 204, 0)
        else:
            color = (255, 0, 0)
        draw.rectangle(
            (
                position[0],
                (
                    position[0][0]
                    + (position[1][0] - position[0][0]) * disk_usage_percent / 100,
                    position[1][1],
                ),
            ),
            fill=color,
        )
        text = "Disk"
        font, text_width, text_height = await self.get_font_box(35, text)
        draw.text(
            (70, 795),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"{disk_usage}GB / {disk_total}GB"
        font, text_width, text_height = await self.get_font_box(35, text)
        # 写在矩形中间
        draw.text(
            (
                position[0][0] + (position[1][0] - position[0][0]) / 2 - text_width / 2,
                position[0][1]
                + (position[1][1] - position[0][1]) / 2
                - text_height / 2,
            ),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 网络信息 -----------------------------------

        net_sent, net_recv = await self.get_network_info()
        text = "Network"
        font, text_width, text_height = await self.get_font_box(35, text)
        draw.text(
            (70, 855),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = f"↑ {net_sent}MB/s  | ↓ {net_recv}MB/s"
        font, text_width, text_height = await self.get_font_box(35, text)
        draw.text(
            (720 - text_width, 855),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 任务信息 -----------------------------------

        tasks = await self.get_task_info()
        task_names = [task["name"] for task in tasks]
        task_memory_usages = [task["memory_usage"] for task in tasks]
        text = "\n".join(task_names)
        font, text_width, text_height = await self.get_font_box(35, text)
        draw.text(
            (70, 955),
            text,
            font=font,
            fill=(0, 0, 0),
        )
        text = "\n".join(
            [f"{task_memory_usage}MB" for task_memory_usage in task_memory_usages]
        )
        font, text_width, text_height = await self.get_font_box(35, text)
        draw.text(
            (530, 955),
            text,
            font=font,
            fill=(0, 0, 0),
        )

        # ----------------------------------- 收个尾 -----------------------------------

        background_img_name = template.name.split(".")[0]
        text = f"Nonebot2 × Status | Cpython {platform.python_version()} | Background is {background_img_name} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        font, text_width, text_height = await self.get_font_box(18, text)
        draw.text(
            (400 - text_width / 2, 1320),
            text,
            font=font,
            fill=(0, 255, 255),
        )

        # ----------------------------------- 返回图片 -----------------------------------

        byte_data = BytesIO()
        img.save(byte_data, "png")
        return byte_data.getvalue()

    async def get_font_box(
        self, size: int, text: str
    ) -> Tuple[ImageFont.FreeTypeFont, int, int]:
        """传入文字大小和内容, 获取字体和字体框"""
        font = ImageFont.truetype(str(self.module_path / "font" / self.font), size)
        _, _, text_width, text_height = font.getbbox(text)
        return font, text_width, text_height

    @staticmethod
    async def get_bot_avatar(bot_id) -> Union[bytes, None]:
        """获取头像"""
        async with AsyncClient() as client:
            r = await client.get(f"https://q1.qlogo.cn/g?b=qq&nk={bot_id}&s=640")
            if r.status_code == 200:
                return r.content

    @staticmethod
    async def get_cpu_status() -> Tuple[float, int, int, float, str]:
        """获取当前CPU使用情况, 返回值为元组, 第一个为使用百分比, 第二个为逻辑CPU数量, 第三个为物理CPU数量, 第四个为最大频率, 第五个为CPU型号"""
        cpu_usage = psutil.cpu_percent(interval=0.5)
        cpu_logical_count = psutil.cpu_count()
        cpu_count = psutil.cpu_count(logical=False)
        cpu_max_frequency = 0.0
        if platform.system() == "Windows":
            cpu_max_frequency = psutil.cpu_freq().max
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("cpu MHz"):
                    cpu_max_frequency = float(line.split(":")[-1])
                    break
        cpu_models = cpuinfo.get_cpu_info()["brand_raw"].split(" ")
        cpu_model = cpu_models[cpu_models.index("CPU") - 1]
        return cpu_usage, cpu_logical_count, cpu_count, cpu_max_frequency, cpu_model

    @staticmethod
    async def get_memory_status() -> Tuple[float, float, float, float]:
        """获取当前内存使用情况, 返回值为元组, 第一个为使用百分比, 第二个为总容量, 第三个为已用容量, 第四个为剩余容量"""
        mem_total = psutil.virtual_memory().total
        mem_usage_percent = psutil.virtual_memory().percent
        mem_free = psutil.virtual_memory().free
        mem_usage = mem_total * mem_usage_percent / 100
        return (
            mem_usage_percent,
            round(mem_total / 1024**3, 2),
            round(mem_usage / 1024**3, 2),
            round(mem_free / 1024**3, 2),
        )

    @staticmethod
    async def get_virtual_memory() -> Tuple[float, float, float, float]:
        """获取当前虚拟内存使用情况, 返回值为元组, 第一个为使用百分比, 第二个为总容量, 第三个为已用容量, 第四个为剩余容量"""
        mem_total = psutil.swap_memory().total
        mem_usage_percent = psutil.swap_memory().percent
        mem_free = psutil.swap_memory().free
        mem_usage = mem_total * mem_usage_percent / 100
        return (
            mem_usage_percent,
            round(mem_total / 1024**3, 2),
            round(mem_usage / 1024**3, 2),
            round(mem_free / 1024**3, 2),
        )

    @staticmethod
    async def get_disk_info() -> Tuple[float, float, float]:
        """获取当前磁盘使用情况, 返回值为元组, 第一个为使用百分比, 第二个为总容量, 第三个为已用容量, 第四个为剩余容量"""
        disk_usage = psutil.disk_usage("/")
        disk_usage_percent = disk_usage.percent
        disk_total = disk_usage.total
        disk_usage = disk_usage.used
        return (
            disk_usage_percent,
            round(disk_total / 1024**3, 2),
            round(disk_usage / 1024**3, 2),
        )

    @staticmethod
    async def get_network_info() -> Tuple[float, float]:
        """获取当前网络上下行速度, 第一个为上行速度, 第二个为下行速度"""
        net_io = psutil.net_io_counters()
        net_sent = net_io.bytes_sent
        net_recv = net_io.bytes_recv
        await asyncio.sleep(0.5)
        net_io = psutil.net_io_counters()
        net_sent = net_io.bytes_sent - net_sent
        net_recv = net_io.bytes_recv - net_recv
        return round(net_sent / 1024**2, 2), round(net_recv / 1024**2, 2)

    @staticmethod
    async def get_task_info() -> List[Dict]:
        """获取当前任务, 获取占用内存最多的八个进程"""
        tasks = []
        for proc in psutil.process_iter():
            with contextlib.suppress(psutil.NoSuchProcess):
                tasks.append(
                    {
                        "name": proc.name(),
                        "memory_usage": round(proc.memory_info().rss / 1024**2, 2),
                    }
                )
        tasks.sort(key=lambda x: x["memory_usage"], reverse=True)
        return tasks[:8]

    async def get_run_time(self) -> Tuple[str, str]:
        """获取当前系统运行事件以及程序运行时间"""
        run_time = time.time() - self.start_time
        program_run_time = (
            f"{int(run_time // 3600)}:{int(run_time % 3600 // 60)}:{int(run_time % 60)}"
        )
        uptime_seconds = int(
            (
                datetime.datetime.now()
                - datetime.datetime.fromtimestamp(psutil.boot_time())
            ).total_seconds()
        )
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime_seconds %= 60
        return f"{uptime_hours}:{uptime_minutes}:{uptime_seconds}", program_run_time


status = Status()

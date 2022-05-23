import random
from typing import Tuple, List, Dict, Union, Optional
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import asyncio
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment
from .config import tkk_config, TKK_PATH

class RandomTkkHandler:
    
    def __init__(self):
        self.tkk_config = tkk_config
        self.timers: Dict[str, asyncio.TimerHandle] = dict()
        self.tkk_status: Dict[str, Union[bool, str, List[int], bytes]] = dict()
        
    def config_tkk_size(self, level: str) -> int:
        '''
            size of tkk picture
        '''
        if level == "简单":
            return self.tkk_config.easy_size
        elif level == "普通":
            return self.tkk_config.normal_size
        elif level == "困难":
            return self.tkk_config.hard_size
        elif level == "地狱":
            return self.tkk_config.extreme_size
        else:
            try:
                tkk_size = int(level) if int(level) <= self.tkk_config.max_size else self.tkk_config.normal_size
                if tkk_size < self.tkk_config.easy_size:
                    tkk_size = self.tkk_config.easy_size
                return tkk_size
            except:
                return self.tkk_config.easy_size
    
    def get_tkk_position(self, tkk_size: int) -> Tuple[int, int]:
        '''
            生成唐可可坐标
        '''
        col = random.randint(1, tkk_size)   # 列
        row = random.randint(1, tkk_size)   # 行
        print("\n"+"col:"+str(col)+"    row:"+str(row)+"\n")
        return row, col
    
    def get_waiting_time(self, tkk_size: int) -> int:
        '''
            计算等待时间
        '''
        if tkk_size >= 30:
            time = int(0.1 * (tkk_size - 30)**2 + 50)
        else:
            time = int(1.7 * (tkk_size - 10) + 15)
        
        return time
    
    def check_tkk_playing(self, uuid: str) -> bool:
        '''
            作为Rule: 群聊/私聊是否进行游戏
        '''
        if not self.tkk_status.get(uuid, False):
            return False
        else:
            return self.tkk_status[uuid]["playing"]

    def check_starter(self, gid: Optional[str], uid: str) -> bool:
        '''
            作为Rule: 是否为发起者提前结束游戏
        '''
        try:
            if gid is None:
                return self.tkk_status[uid]["playing"] and self.tkk_status[uid]["starter"] == uid
            else:
                return self.tkk_status[gid]["playing"] and self.tkk_status[gid]["starter"] == uid
        except:
            return False
    
    async def draw_tkk(self, row: int, col: int, tkk_size: int) -> Tuple[bytes, bytes]:
        '''
            画图
        '''
        temp = 0
        font: ImageFont.FreeTypeFont = ImageFont.truetype(str(TKK_PATH / "msyh.ttc"), 16)
        base = Image.new("RGB",(64 * tkk_size, 64 * tkk_size))
        
        for r in range(0, tkk_size):
            for c in range(0, tkk_size):
                if r == row - 1 and c == col - 1:
                    tkk = Image.open(TKK_PATH / "tankuku.png")
                    tkk = tkk.resize((64, 64), Image.ANTIALIAS)      #加载icon
                    if self.tkk_config.show_coordinate:
                        draw = ImageDraw.Draw(tkk)
                        draw.text((20,40), f"({c+1},{r+1})", font=font, fill=(255, 0, 0, 0))
                    base.paste(tkk, (r * 64, c * 64))
                    temp += 1
                else:
                    try:
                        icon = Image.open(TKK_PATH /(str(random.randint(1, 22)) + '.png'))
                        icon = icon.resize((64,64), Image.ANTIALIAS)
                        if self.tkk_config.show_coordinate:
                            draw = ImageDraw.Draw(icon)
                            draw.text((20,40), f"({c+1},{r+1})", font=font, fill=(255, 0, 0, 0))
                        base.paste(icon, (r * 64, c * 64))
                    except:
                        continue
        
        buf = BytesIO()
        base.save(buf, format='png')
        
        base2 = base.copy()
        mark = Image.open(TKK_PATH / "mark.png")

        base2.paste(mark,((row - 1) * 64, (col - 1) * 64), mark)
        buf2 = BytesIO()
        base2.save(buf2, format='png')
        
        return buf.getvalue(), buf2.getvalue()
    
    def check_answer(self, uuid: str, pos: List[int]) -> bool: 
        return pos == self.tkk_status[uuid]["answer"]
    
    async def surrender(self, matcher: Matcher, uuid: str) -> None:
        '''
            发起者主动提前结束游戏：取消定时器，结算游戏
        '''
        try:
            timer = self.timers.get(uuid, None)
            if timer:
                timer.cancel()
        except:
            return False
        
        await self.timeout_close_game(matcher, uuid)
    
    async def timeout_close_game(self, matcher: Matcher, uuid: str) -> None:
        '''
            超时无正确答案，结算游戏: 移除定时器、公布答案
        '''
        self.timers.pop(uuid, None)
        answer = self.tkk_status[uuid]["answer"]
        msg = "没人找出来，好可惜啊☹\n" + f"答案是{answer[0]}行{answer[1]}列" + MessageSegment.image(self.tkk_status[uuid]["mark_img"])
             
        if not self.tkk_status.pop(uuid, False):
            await matcher.finish("提前结束游戏出错……")
        
        await matcher.finish(msg)

    def start_timer(self, matcher: Matcher, uuid: str, timeout: int) -> None:
        '''
            开启超时定时器 回调函数timeout_close_game
        '''
        timer = self.timers.get(uuid, None)
        if timer:
            timer.cancel()
        loop = asyncio.get_running_loop()
        timer = loop.call_later(
            timeout, lambda: asyncio.ensure_future(self.timeout_close_game(matcher, uuid))
        )
        self.timers[uuid] = timer
        
    def binggo_close_game(self, uuid: str) -> bool:
        '''
            等待时间内答对后结束游戏：取消定时器，移除定时器，移除记录
        '''
        try:
            timer = self.timers.get(uuid, None)
            if timer:
                timer.cancel()
            self.timers.pop(uuid, None)
        except:
            return False
        
        return self.tkk_status.pop(uuid, False)
    
    async def one_go(self, matcher: Matcher, uuid: str, uid: str, level: str) -> Tuple[bytes, int]:
        '''
            记录每个群组如下属性：
                "playing": False,       bool        当前是否在进行游戏
                "starter": Username,    str         发起此次游戏者，仅此人可提前结束游戏
                "anwser": [0, 0],       List[int]   答案
                "mark_img": bytes       bytes       框出唐可可的图片
        '''
        tkk_size = self.config_tkk_size(level)
        row, col = self.get_tkk_position(tkk_size)
        waiting = self.get_waiting_time(tkk_size)
        img_file, mark_file = await self.draw_tkk(row, col, tkk_size)
        
        self.tkk_status[uuid] = {
            "playing": True,
            "starter": uid,
            "answer": [col, row],
            "mark_img": mark_file
        }

        # 开启倒计时
        self.start_timer(matcher, uuid, waiting)
        return img_file, waiting

random_tkk_handler = RandomTkkHandler()
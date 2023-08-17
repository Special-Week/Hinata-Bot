import asyncio
import contextlib
import os
import platform
import random
from re import sub
from typing import Tuple

import nonebot
from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup

from .config import config
from .get_data import get_setu
from .setu_message import setu_sendcd, setu_sendmessage
from .utils import setu_help, utils


class SetuHandle:
    def __init__(self) -> None:
        self.max_num = config.setu_max_num      # 最大数量
        self.cd_dir = {}                        # cd字典
        self.cd_time = config.setu_cd           # cd时间
        self.withdraw_time = config.setu_withdraw_time      # 撤回时间


    async def number_check(
        self,
        num: int,
        matcher: Matcher,
        event: MessageEvent,
    ):
        qid = event.get_user_id()
        # 色图图片质量, 如果num为3-6质量为70,如果num为7-max质量为50,其余为95(图片质量太高发起来太费时间了)
        # 注:quality值95为原图
        if num >= 3 and num <= 6:
            quality = 70
        elif num >= 7:
            quality = 50
        else:
            quality = 95
        if num >= 3:
            await matcher.send(f"由于数量过多请等待\n当前图片质量为{quality}\n3-6:quality = 70\n7-{self.max_num}:quality = 50")
        # 记录cd
        self.cd_dir.update({qid: event.time})
        return quality

    async def cd_allow(
        self,
        key,
        r18,
        bot: Bot,
        num: int,
        flag_log: str,
        matcher: Matcher,
        event: MessageEvent,
    ):
        quality = await self.number_check(num, matcher, event)
        # data是数组套娃, 数组中的每个元素内容为: [图片, 信息, True/False, url]
        try:
            data = await get_setu.get_setu(num, quality, r18, key)
        except Exception as e:
            await matcher.finish(f"Error: {str(e)}")

        
        # 发送的消息列表
        message_list = []
        for pic in data:
            # 如果状态为True,说明图片拿到了
            if pic[2]:
                message = f"{random.choice(setu_sendmessage)}{flag_log}" + \
                            Message(pic[1]) + MessageSegment.image(pic[0])
                flag_log = ""
            else:
                message = pic[0] + pic[1]
            message_list.append(message)
        # 为后面撤回消息做准备
        setu_msg_id = []
        # 尝试发送
        try:
            if isinstance(event, PrivateMessageEvent):
                # 私聊直接发送
                for msg in message_list:
                    setu_msg_id.append((await matcher.send(msg))['message_id'])
            elif isinstance(event, GroupMessageEvent):
                # 群聊以转发消息的方式发送
                msgs = [utils.to_json(msg, bot.self_id, "setu-bot")
                        for msg in message_list]
                setu_msg_id.append((await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs))['message_id'])

        # 发送失败
        except Exception as e:
            # logger以及移除cd
            logger.warning(e)
            self.cd_dir.pop(event.get_user_id())
            await matcher.finish(
                message=Message(f"消息被风控了捏，图发不出来，请尽量减少发送的图片数量尝试捕获错误信息: {str(e)}"),
                at_sender=True,
            )

        # 自动撤回涩图
        if self.withdraw_time != 0:
            with contextlib.suppress(Exception):
                await asyncio.sleep(self.withdraw_time)
                for msg_id in setu_msg_id:
                    await bot.delete_msg(message_id=msg_id)


    async def cd_notallow(
        self,
        cd,
        matcher: Matcher,
    ):
        time_last = self.cd_time - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{f'{str(hours)}小时' if hours else ''}{f'{str(minutes)}分钟' if minutes else ''}{f'{str(seconds)}秒' if seconds else ''}"

        await matcher.send(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}", at_sender=True)



    async def r18_ban_check(
        self,
        num,
        r18flag,
        matcher: Matcher,
        event: MessageEvent,
    ):
        # 私聊的话暂且让他按照输入的来
        r18 = bool((isinstance(event, PrivateMessageEvent) and r18flag))
        # 获取会话id, 有群号有qq号
        sid = event.get_session_id()
        # 遍历banlist
        for session_id in utils.banlist:
            if session_id in sid:
                await matcher.finish("涩图功能已在此会话中禁用！")
        if num > self.max_num or num < 1:
            await matcher.finish(f"数量需要在1-{self.max_num}之间")
        # 如果r18是false的话在进行r18list判断
        if not r18:
            for groubnumber in utils.r18list:
                if groubnumber in sid:
                    r18 = bool(r18flag)
        return r18



    async def main(
        self,
        bot: Bot, 
        matcher: Matcher,
        event: MessageEvent, 
        args: Tuple = RegexGroup()
    ):
        r18flag = args[2]
        key = args[3]                 # 获取关键词参数
        key = sub('[\'\"]', '', key)  # 去掉引号防止sql注入
        num = args[1]          # 获取数量参数
        num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", num)) if num else 1

        qid = event.get_user_id()
        try:
            cd = event.time - self.cd_dir[qid]
        except KeyError:
            cd = self.cd_time + 1
        r18 = await self.r18_ban_check(num, r18flag, matcher, event)

        # key按照空格切割为数组, 用于多关键词搜索, 并且把数组中的空元素去掉
        key = key.split(" ")
        key = [word.strip() for word in key if word.strip()]

        flag_log = (
            f"\nR18 == {str(r18)}\nkeyword == {key}\nnum == {num}\n"
            if key
            else f"\nR18 == {str(r18)}\nkeyword == NULL\nnum == {num}\n"
        )
        logger.info(f"key = {key}\tr18 = {r18}\tnum = {num}")       # 控制台输出
        # cd判断,superusers无视cd
        if (
            cd > self.cd_time
            or event.get_user_id() in nonebot.get_driver().config.superusers
        ):
            await self.cd_allow(key, r18, bot, num, flag_log, matcher, event)
        # cd还没过的情况
        else:
            await self.cd_notallow(cd, matcher)





    async def add_r18list(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        # 获取消息文本
        msg = arg.extract_plain_text().strip().split()[0]
        # 如果不是数字就返回
        if not msg.isdigit():
            await matcher.finish(f"ID:{msg}不是数字")
        # 如果已经存在就返回
        if msg in utils.r18list:
            await matcher.finish(f"ID:{msg}已存在")
        utils.r18list.append(msg)
        # 写入文件
        utils.config.update({"r18list": utils.r18list})
        utils.write_configjson()
        await matcher.finish(f"ID:{msg}添加成功")



    async def del_r18list(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        # 获取消息文本
        msg = arg.extract_plain_text().strip()
        try:    
            utils.r18list.remove(msg)
        except ValueError:          # 如果不存在就返回
            await matcher.finish(f"ID:{msg}不存在")
        # 写入文件
        utils.config.update({"r18list": utils.r18list})    # 更新dict
        utils.write_configjson()                        # 写入文件
        await matcher.finish(f"ID:{msg}删除成功")


    async def get_r18list(
        self,
        matcher: Matcher,
    ):
        await matcher.finish("R18名单：\n" + str(utils.r18list))


    async def setu_help(
        self,
        matcher: Matcher,
    ):
        await matcher.finish(setu_help)   # 发送



    async def admin_ban_setu(
        self,
        matcher: Matcher,
        event: GroupMessageEvent
    ):
        gid: str = str(event.group_id)
        # 如果存在
        if gid in utils.banlist:
            await matcher.finish(f"ID:{gid}已存在")
        utils.banlist.append(gid)
        utils.config.update({"banlist": utils.banlist})        # 更新dict
        utils.write_configjson()                              # 写入文件
        await matcher.finish(f"ID:{gid}禁用成功, 恢复需要找superuser")


    async def su_ban_setu(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        # 获取消息文本
        msg = arg.extract_plain_text().strip()
        if not msg.isdigit():
            await matcher.finish(f"ID:{msg}不是数字")
        # 如果已经存在就返回
        if msg in utils.banlist:
            await matcher.finish(f"ID:{msg}已存在")
        utils.banlist.append(msg)            # 添加到list
        utils.config.update({"banlist": utils.banlist})    # 更新dict
        utils.write_configjson()              # 写入文件
        await matcher.finish(f"ID:{msg}禁用成功")



    async def disactivate(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ):
        # 获取消息文本
        msg = arg.extract_plain_text().strip()
        try:
            utils.banlist.remove(msg) # 如果不存在就直接finish
        except ValueError:
            await matcher.finish(f"ID:{msg}不存在")
        utils.config.update({"banlist": utils.banlist})    # 更新dict 
        utils.write_configjson()                # 写入文件
        await matcher.finish(f"ID:{msg}解除成功")



    async def set_proxy(self, proxy):
        utils.config.update({"setu_proxy": proxy})
        utils.write_configjson()
        plat = platform.system().lower()    # 获取系统
        if plat == 'windows':
            result = os.popen(f"ping {proxy}").read()  # windows下的ping
        elif plat == 'linux':   
            result = os.popen(f"ping -c 4 {proxy}").read() # linux下的ping
        return result


    async def replace_proxy_got(
        self,
        matcher: Matcher,
        event: MessageEvent
    ):
        msg: str = str(event.get_message())  # 获取消息文本
        if not msg or msg.isspace():
            await matcher.finish("需要输入proxy")
        await matcher.send(f"{msg}已经替换, 正在尝试ping操作验证连通性") # 发送消息
        result = await self.set_proxy(msg.strip())
        await matcher.send(f"{result}\n如果丢失的数据比较多, 请考虑重新更换代理")  # 发送消息

    async def replace_proxy(
        self,
        matcher: Matcher, 
        arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()  # 获取消息文本
        if not msg or msg.isspace():
            await matcher.pause(f"请输入你要替换的proxy, 当前proxy为:{utils.read_proxy()}\ntips: 一些也许可用的proxy\ni.pixiv.re\nsex.nyan.xyz\npx2.rainchan.win\npximg.moonchan.xyz\npiv.deception.world\npx3.rainchan.win\npx.s.rainchan.win\npixiv.yuki.sh\npixiv.kagarise.workers.dev\npixiv.a-f.workers.dev\n等等....\n\neg:px2.rainchan.win\n警告:不要尝试命令行注入其他花里胡哨的东西, 可能会损伤你的电脑")
        else:
            await matcher.send(f"{msg}已经替换, 正在尝试ping操作验证连通性") # 发送消息
            result = await self.set_proxy(msg)
            await matcher.finish(f"{result}\n如果丢失的数据比较多, 请考虑重新更换代理")  # 发送消息



setu_handle = SetuHandle()
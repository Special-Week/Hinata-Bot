from nonebot import on_command
import nonebot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
import requests
from bs4 import BeautifulSoup
from httpx import AsyncClient
import re
import random


# 一次性最多返回多少条结果, 可在env设置
try:
    max_num = nonebot.get_driver().config.magnet_max_num
except:
    max_num = 3

# cookie
try:
    cookie = nonebot.get_driver().config.clm_cookie
except:
    cookie = "challenge=8b11e0a1c25a29ca8cd6b530e64c5294; ex=1; _ga=GA1.1.1219749203.1655966067; _ga_W7KV15XZN0=GS1.1.1655966067.1.1.1655966427.0"

# 我也不知道有没有必要加这一行, 我看着从env闯进来的cookie这个数据类型好像不太对劲
cookie = cookie

# 访问头
headers = {
    "cookie":cookie,
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
}
# 网站主页
magnet_url = "https://clm9.me/"


# 声明一个响应器
bt = on_command("磁力搜索",aliases={'bt'}, priority=10, block=True)

@bt.handle()
async def _(msg: Message = CommandArg()):
    # 纯文本提取
    keyword = msg.extract_plain_text()
    search_url = f"https://clm9.me/search?word={keyword}"
    try:
        # 尝试获取消息
        message = await get_magnet(search_url)
    except:
        # 获取失败的时候返回错误信息
        await bt.finish("搜索失败, 可能网络出现问题, 也可能env配置的cookie过期了")
    # 如果搜索到了结果, 则尝试发送, 有些账号好像文本太长cqhttp会显示风控
    if message:
        try:
            await bt.send(message)
        except:
            await bt.finish("消息被风控了, message发送失败")
    else:
        await bt.finish("没有找到结果捏")
        




# 获取磁力链接和一堆东西
async def get_magnet(url):
    # 声明一个列表和要发送消息的字符串
    message_list = []
    message=""
    async with AsyncClient() as client:
        # 发送请求
        res = await client.get(url=url, headers=headers, timeout=30)
        res=res.text
        soup = BeautifulSoup(res, "lxml")
        # 这好像是Search_box, 不懂捏
        item_lst = (soup.find_all("div", {"class": "Search_box"}))[0].find_all("div",{"class":"SearchListTitle_list_title"})
        # 遍历每个box
        for item in item_lst:
            # 通过box的href内容获取url
            url = magnet_url + (item.find("a"))['href']
            # 访问新的url
            res = requests.get(url, headers=headers)
            res = res.text
            soup = BeautifulSoup(res, "lxml")
            magnet_lst = soup.find_all("div", {"class": "Information_l_content"})
            # 提取Information_l_content的内容
            size = str(list(magnet_lst[1])[4])
            size = re.sub(u"\\<.*?\\>", "", size)       # 这个是文件大小
            magnet = (magnet_lst[0].find("a"))['href']  # 这个是磁力链接
            # 访问File_list_info, 目的是为了获取文件名
            name = soup.find_all('div',{'class':'File_list_info'})
            name = list(name[0])[0]
            # 字符串拼接并且添加到列表
            message_list.append(f"文件名: {name} \n大小: {size}\n链接: {magnet}\n")
    # num是每次发送的条数        
    num = max_num
    # 防止数组越界
    if len(message_list) < max_num:
        num = len(message_list)
    # 随机选择一些条目 
    message_list = random.sample(message_list, num)
    # message拼接
    for msg in message_list:
        message = message + msg + "\n"
    # 在控制台输出一下
    print(message)
    return message
        

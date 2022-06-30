import nonebot
import os
from nonebot.log import logger
# 色图cd容器
cd_dir = {}

# setu cd,可在env设置,默认20s,类型int
try:
    cdTime = nonebot.get_driver().config.setu_cd
except:
    cdTime = 20

# setu_ban名单,可在env设置,类型string列表
try:
    banlist = nonebot.get_driver().config.setu_ban
except:
    banlist = []

# 撤回时间,可在env设置,默认100s,类型int
try:
    withdraw_time = nonebot.get_driver().config.setu_withdraw_time
except:
    withdraw_time = 100

# 一次最大多少张图片,可在env设置,默认10张,类型int
try:
    max_num = nonebot.get_driver().config.setu_max_num
except:
    max_num = 10


# 先读一读试试
try:
    fp = open('data/youth-version-of-setu4/r18list.txt')
    fp.close()
# 没有的话咱就新建
except:
    # 尝试新建data文件夹
    try:
        os.makedirs('data/youth-version-of-setu4')
    except FileExistsError:
        logger.info('data/youth-version-of-setu4文件夹已存在')
    except Exception as e:
        raise Exception(f'无法新建data/youth-version-of-setu4文件夹, 请检查您的工作路径及读写权限!\n{e}')
    fp = open('data/youth-version-of-setu4/r18list.txt', 'w')
    fp.write("114514\n")
    fp.close()


r18list = []
with open('data/youth-version-of-setu4/r18list.txt', 'r') as fp:
    while True:
        line = fp.readline()
        if not line:
            break
        r18list.append(line.strip("\n"))

def to_json(msg, name: str, uin: str):
    return {
        'type': 'node',
        'data': {
            'name': name,
            'uin': uin,
            'content': msg
        }
    }

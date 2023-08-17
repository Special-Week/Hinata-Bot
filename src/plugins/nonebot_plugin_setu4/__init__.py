from re import I

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import GROUP, PRIVATE_FRIEND
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

from .handle import setu_handle

# 主功能响应器
on_regex(
    r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
    priority=10,
    block=True,
    handlers=[setu_handle.main],
)

# r18列表添加用的,权限SUPERSUSER
on_command(
    "add_r18", 
    permission=SUPERUSER,
    block=True, priority=10,
    handlers=[setu_handle.add_r18list]
)


# r18列表删除用的,权限SUPERSUSER
on_command(
    "del_r18", 
    permission=SUPERUSER, 
    block=True, 
    priority=10,
    handlers=[setu_handle.del_r18list]
)

# 查看r18名单
on_command(
    "r18名单", 
    permission=SUPERUSER,
    block=True, 
    priority=10,
    handlers=[setu_handle.get_r18list]
)

# 色图功能帮助
on_command(
    "setu_help", 
    block=True, 
    priority=9,
    handlers=[setu_handle.setu_help]
)

# 禁用色图功能
on_command(
    "ban_setu", 
    aliases={"setu_ban", "禁用色图"}, 
    permission=GROUP_OWNER | GROUP_ADMIN, 
    priority=9, 
    block=True,
    handlers=[setu_handle.admin_ban_setu]
)

on_command(
    "ban_setu", 
    aliases={"setu_ban", "禁用色图"}, 
    permission=SUPERUSER, 
    priority=8, 
    block=True,
    handlers=[setu_handle.su_ban_setu]
)



# 解除禁用色图功能
on_command(
    "disactivate", 
    aliases={"解除禁用"}, 
    permission=SUPERUSER, 
    priority=9, 
    block=True,
    handlers=[setu_handle.disactivate]
)

# 更换代理
on_command(
    "更换代理", 
    aliases={"替换代理", "setu_proxy"}, 
    permission=SUPERUSER, 
    block=True, 
    priority=9,
    handlers=[setu_handle.replace_proxy, setu_handle.replace_proxy_got]
)

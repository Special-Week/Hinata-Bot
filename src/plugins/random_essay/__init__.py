from nonebot import on_command
from .handle import essay



on_command("随机小作文",aliases={"发病小作文"}, block=True, handlers=[essay.main])


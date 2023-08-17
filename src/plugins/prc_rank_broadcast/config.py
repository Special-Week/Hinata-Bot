from nonebot import get_driver
from pydantic import BaseSettings


class Config(BaseSettings):
    guild_default_switch: bool = True
    interval: int = 5

    class Config:
        extra = "ignore"


config: Config = Config.parse_obj(get_driver().config)

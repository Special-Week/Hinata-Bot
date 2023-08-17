import json
from pathlib import Path
from typing import Union

from nonebot import get_driver
from pydantic import BaseSettings


class Config(BaseSettings):
    setu_cd: int = 30
    setu_withdraw_time: int = 100
    setu_max_num: int = 10
    config_path: Path = Path("data/youth-version-of-setu4")
    config_file: Path = config_path / "config.json"
    setu_save: Union[bool, str] = False

    class Config:
        extra = "ignore"


config = Config.parse_obj(get_driver().config)
if not config.config_path.exists():
    config.config_path.mkdir(parents=True, exist_ok=True)


if not config.config_file.exists():
    config_json = {
        "r18list": [],
        "banlist": [],
        "setu_proxy": "i.pixiv.re"
    }
    with open(config.config_file, "w", encoding="utf-8") as f:
        json.dump(config_json, f, indent=4, ensure_ascii=False)

from pydantic import BaseModel, Extra
from pathlib import Path
import os
from nonebot.log import logger
import nonebot

class RandomTkkConfig(BaseModel, extra=Extra.ignore):
    
    tkk_path: str = os.path.join(os.path.dirname(__file__), "resource")
    easy_size:  int = 10
    normal_size: int = 20
    hard_size: int = 40
    extreme_size: int = 60
    max_size: int = 80
    show_coordinate: bool = True
    
driver = nonebot.get_driver()
tkk_config: RandomTkkConfig = RandomTkkConfig.parse_obj(driver.config.dict())
TKK_PATH: Path = Path(tkk_config.tkk_path)
TKK_RESOURCE_ALL: bool = True

@driver.on_startup
async def check_tkk_resource():
    global TKK_PATH, TKK_RESOURCE_ALL
    
    if not TKK_PATH.exists():
        TKK_RESOURCE_ALL = False

    if not (TKK_PATH / "tankuku.png").exists() or not (TKK_PATH / "mark.png").exists() or not (TKK_PATH / "msyh.ttc").exists():
        TKK_RESOURCE_ALL = False
        
    for i in range(1, 23):
        if not (TKK_PATH / (str(i) + ".png")).exists():
            TKK_RESOURCE_ALL = False

    if not TKK_RESOURCE_ALL:
        logger.warning("随机唐可可资源不完整或路径错误，请检查！")

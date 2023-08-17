import json
from pathlib import Path
from typing import List

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher


class WordleHelp:
    def __init__(self) -> None:
        """初始化, 读取单词列表"""
        plugin_path = Path(__file__).parent
        with open(plugin_path / "data.json",'r', encoding='utf-8') as f:
            self.words: List[str] = json.load(f)

    async def get_matching_words(self, target: str) -> List[str]:
        """获取匹配的单词"""
        return [word for word in self.words if len(word) == len(target) and all(target[i] == "_" or word[i] == target[i] for i in range(len(word)))]
    
    async def main(
        self,
        matcher: Matcher,
        event: MessageEvent
    ) -> None:
        """处理消息"""
        target = event.get_message().__str__().strip().split("#")       # 按照#分割成列表, 理论上最多两个元素, 前者为目标单词, 后者排除的字母
        matching_words = await self.get_matching_words(target[0])       # 先匹配单词
        if len(target) == 2:                                            # 如果有排除的字母, 则再次筛选
            matching_words = [word for word in matching_words if not set(word) & set(target[1])]

        if len(matching_words) == 0:                                    # 如果没有匹配到单词, 则返回
            await matcher.send("没有匹配到单词捏")
        elif len(matching_words) > 50:                                  # 如果匹配到的单词太多, 则返回
            await matcher.send("匹配到的单词太多了(>50), 建议您缩小一下范围")
        else:                                                           # 返回匹配到的单词
            await matcher.send(
                "以下是匹配到的单词：\n"+
                "\n".join(matching_words)
            )
            
wordle_help = WordleHelp()

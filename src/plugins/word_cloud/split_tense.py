import re
from typing import Dict

import jieba.posseg as pseg
import spacy


class SplitTense:
    def __init__(self) -> None:
        self.nlp = spacy.load("en_core_web_sm")
        self.chinese_pattern = re.compile(r"[\u4e00-\u9fa5]")

    async def split_tense(self, text: str) -> Dict[str, int]:
        """分析text的词性"""
        target = []
        words = pseg.cut(text)
        target += [
            word.word
            for word in words
            if (word.flag.startswith("n") or word.flag.startswith("v"))
            and len(word.word) > 1
        ]
        cleaned_text = await self.clean_text(text)
        doc = self.nlp(cleaned_text)
        target += [token.text for token in doc if token.pos_ in ["NOUN", "VERB"] and len(token.text) > 1]
        data = {}
        for i in target:
            if i not in data:
                data[i] = 0
            data[i] += 1
        return data

    async def clean_text(self, text: str) -> str:
        """去除text的汉字"""
        return re.sub(self.chinese_pattern, "", text)

split_tool = SplitTense()
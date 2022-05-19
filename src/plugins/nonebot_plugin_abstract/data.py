from nonebot.log import logger
from .emoji import emoji, emoji_py
import jieba
import pinyin

def text_to_emoji(text):
    try:
        text_with_emoji = ''
        text_jieba = jieba.cut(text, cut_all=False)
        for word in text_jieba:
            word = word.strip()
            # 分词检索
            if word in emoji.keys():
                text_with_emoji += emoji[word]
            elif word not in emoji.keys():
                word_py = pinyin.get(word, format="strip")
                # 分词拼音检索
                if word_py in emoji_py.keys():
                    text_with_emoji += emoji_py[word_py]
                else:
                    if len(word) > 0: # if the two characters or more
                        # 单字检索
                        for character in word:
                            if character in emoji.keys():
                                text_with_emoji += emoji[character]
                            else:
                                # 单字拼音检索
                                character_py = pinyin.get(character, format="strip")
                                if character_py in emoji_py.keys():
                                    text_with_emoji += emoji_py[character_py]
                                else:
                                    text_with_emoji += character
                    else: # 只有一个汉字，前面已经检测过字和拼音都不在抽象词典中，直接加词
                        text_with_emoji += word.strip()
    except Exception as e:
        logger.error("文本抽象化失败~")
        raise e
    return text_with_emoji
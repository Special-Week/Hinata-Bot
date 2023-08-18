import os
import time
from typing import Dict

from sqlalchemy import Column, Engine, Integer, String, create_engine, orm
from sqlalchemy.orm import sessionmaker

# 数据库路径
DATA_PATH = "data/wordcloud"

# 不存在则创建文件夹
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)


engine: Engine = create_engine(f"sqlite:///{DATA_PATH}/words.db")
session = sessionmaker(engine)
Base = orm.declarative_base()


class WordData(Base):
    """数据表"""

    __tablename__: str = "wordcloud"

    id = Column(Integer, primary_key=True)
    date = Column(String(20), nullable=False, index=True)
    group_id = Column(Integer, nullable=False, index=True)
    word = Column(String, nullable=False, index=True)
    appeal = Column(Integer, nullable=False)


Base.metadata.create_all(engine)


def get_today() -> str:
    """获取当前年月日格式: 2023-02-04"""
    return time.strftime("%Y-%m-%d", time.localtime())


def get_today_data(group_id: int) -> Dict[str, int]:
    """获取今日数据"""
    with session() as s:
        data = (
            s.query(WordData)
            .filter(WordData.group_id == group_id, WordData.date == get_today())
            .all()
        )
    return {d.word: d.appeal for d in data}


def get_history_data(group_id: int) -> Dict[str, int]:
    """获取历史数据"""
    with session() as s:
        data = s.query(WordData).filter(WordData.group_id == group_id).all()
    target = {}
    for d in data:
        if d.word not in target:
            target[d.word] = 0
        target[d.word] += d.appeal
    return target


def get_week_data(group_id: int) -> Dict[str, int]:
    """获取一周数据"""
    since_day = [
        time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400 * i))
        for i in range(7)
    ]
    with session() as s:
        data = (
            s.query(WordData)
            .filter(WordData.group_id == group_id, WordData.date.in_(since_day))
            .all()
        )
    target = {}
    for d in data:
        if d.word not in target:
            target[d.word] = 0
        target[d.word] += d.appeal
    return target


def insert_data(group_id: int, data: Dict[str, int]):
    """插入数据"""
    with session() as s:
        if (
            not s.query(WordData)
            .filter(WordData.group_id == group_id, WordData.date == get_today())
            .all()
        ):
            for word, appeal in data.items():
                s.add(
                    WordData(
                        date=get_today(),
                        group_id=group_id,
                        word=word,
                        appeal=appeal,
                    )
                )
        else:
            for word, appeal in data.items():
                if (
                    not s.query(WordData)
                    .filter(
                        WordData.group_id == group_id,
                        WordData.date == get_today(),
                        WordData.word == word,
                    )
                    .all()
                ):
                    s.add(
                        WordData(
                            date=get_today(),
                            group_id=group_id,
                            word=word,
                            appeal=1,
                        )
                    )
                else:
                    s.query(WordData).filter(
                        WordData.group_id == group_id,
                        WordData.date == get_today(),
                        WordData.word == word,
                    ).update({WordData.appeal: WordData.appeal + appeal})
        s.commit()

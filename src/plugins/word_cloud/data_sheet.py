import os
import time
from typing import Dict, List, Tuple

from sqlalchemy import (
    Column,
    Engine,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import sessionmaker


class WordData:
    """sqlalchemy操作"""

    def __init__(self):
        DATA_PATH = "data/wordcloud"
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)
        self.engine: Engine = create_engine(
            f"sqlite:///{DATA_PATH}/words.db"
        )  # 创建数据库引擎
        self.session = sessionmaker(self.engine)  # 创建会话
        self.metadata = MetaData()  # 创建元数据
        self.all_table_name: List[str] = inspect(
            self.engine
        ).get_table_names()  # 获取所有表名

        self.switch_table()  # 切换表

    @staticmethod
    def get_today() -> Tuple[str, int]:
        """获取当前年月日格式: [2023-02, 30]"""
        return (
            time.strftime("%Y-%m", time.localtime(time.time())),
            int(time.strftime("%d", time.localtime(time.time()))),
        )

    def switch_table(self) -> None:
        """切换表"""
        current_month: str = self.get_today()[0]
        self.custom_table: Table = Table(
            current_month,
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("date", Integer, nullable=False, index=True),
            Column("group_id", Integer, nullable=False, index=True),
            Column("word", String, nullable=False),
            Column("appeal", Integer, nullable=False),
            extend_existing=True,
        )
        if current_month not in self.all_table_name:  # 如果当前月份不在表名中
            self.custom_table.create(self.engine)
            self.all_table_name.append(self.custom_table.name)

    def insert_data(self, group_id: int, data: Dict[str, int]):
        """插入数据"""
        month, day = self.get_today()  # 获取当前月份和日期
        if month not in self.all_table_name:
            self.switch_table()
        with self.session() as s:
            # 如果这一天群id没有数据, 则直接插入数据
            if (
                not s.query(self.custom_table)
                .filter(
                    self.custom_table.c.date == day,
                    self.custom_table.c.group_id == group_id,
                )
                .all()
            ):
                for k, v in data.items():
                    s.execute(
                        self.custom_table.insert(),
                        [{"date": day, "group_id": group_id, "word": k, "appeal": v}],
                    )
            # 如果这一天群id有数据, 则分情况插入数据
            else:
                for k, v in data.items():
                    # 如果这一天群id有数据, 但是没有这个词, 则直接插入数据
                    if (
                        not s.query(self.custom_table)
                        .filter(
                            self.custom_table.c.date == day,
                            self.custom_table.c.group_id == group_id,
                            self.custom_table.c.word == k,
                        )
                        .all()
                    ):
                        s.execute(
                            self.custom_table.insert(),
                            [
                                {
                                    "date": day,
                                    "group_id": group_id,
                                    "word": k,
                                    "appeal": v,
                                }
                            ],
                        )
                    # 如果这一天群id有数据, 也有这个词, 则更新数据
                    else:
                        s.execute(
                            self.custom_table.update()
                            .where(
                                self.custom_table.c.date == day,
                                self.custom_table.c.group_id == group_id,
                                self.custom_table.c.word == k,
                            )
                            .values(appeal=self.custom_table.c.appeal + v)
                        )
            s.commit()

    def get_today_data(self, group_id: int) -> Dict[str, int]:
        """获取今日数据"""
        day = self.get_today()[1]
        with self.session() as s:
            data = (
                s.query(self.custom_table)
                .filter(
                    self.custom_table.c.date == day,
                    self.custom_table.c.group_id == group_id,
                )
                .all()
            )
        return {d.word: d.appeal for d in data}

    def get_history_data(self, group_id: int) -> Dict[str, int]:
        """获取历史数据"""
        target = {}
        with self.session() as s:
            # 遍历所有表
            for table in self.all_table_name:
                data = s.execute(
                    text(f"select word,appeal from '{table}' where group_id={group_id}")
                )
                # 遍历每个表的数据, target中没有就创造一个值为零, 然后加上这个词的appeal
                for d in data:
                    if d[0] not in target:
                        target[d[0]] = 0
                    target[d[0]] += d[1]
        return target

    def get_week_data(self, group_id: int) -> Dict[str, int]:
        """获取一周数据"""
        day = self.get_today()[1]
        since = day - 7 if day > 8 else day
        target = {}
        with self.session() as s:
            data = (
                s.query(self.custom_table)
                .filter(
                    self.custom_table.c.date >= since,
                    self.custom_table.c.group_id == group_id,
                )
                .all()
            )
        for d in data:
            if d.word not in target:
                target[d.word] = 0
            target[d.word] += d.appeal
        return target

    def get_month_data(self, group_id: int) -> Dict[str, int]:
        """获取一月数据"""
        target = {}
        with self.session() as s:
            data = (
                s.query(self.custom_table)
                .filter(
                    self.custom_table.c.group_id == group_id,
                )
                .all()
            )
        for d in data:
            if d.word not in target:
                target[d.word] = 0
            target[d.word] += d.appeal
        return target


worddata = WordData()

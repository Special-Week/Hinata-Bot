from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    # 配置发件人邮箱
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None

    # 配置收件人邮箱
    receiver_email: Optional[str] = None
    # 重发次数
    retry_count: int = 3

    class Config:
        extra = "ignore"

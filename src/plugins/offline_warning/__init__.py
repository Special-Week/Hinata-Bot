import asyncio
import contextlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot

from .config import Config

config = Config.parse_obj(get_driver().config)

if (
    isinstance(config.sender_email, str)
    and isinstance(config.sender_password, str)
    and isinstance(config.receiver_email, str)
):
    is_configured = True
else:
    is_configured = False
    logger.error("sender_email, sender_password, receiver_email 其中有至少一个未配置，邮件功能将无法使用")


driver = get_driver()


def send_email(bot_id) -> None:
    message = MIMEMultipart()
    message["From"] = config.sender_email
    message["To"] = config.receiver_email
    message["Subject"] = "你的bot掉线了，快去看看吧"
    body = f"你的bot，账号：{bot_id}掉线了，快去看看吧"
    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    for _ in range(config.retry_count):
        try:
            server.login(config.sender_email, config.sender_password)  # type: ignore
            server.sendmail(config.sender_email, config.receiver_email, message.as_string())  # type: ignore
            server.quit()
            break
        except Exception as e:
            logger.error("Error sending email:", e)


@driver.on_bot_disconnect
async def _(bot: Bot) -> None:
    if not is_configured:
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email, bot.self_id)


with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata

    __plugin_meta__ = PluginMetadata(
        name="offline_warning",
        description="nonebot2机器人掉线警告",
        usage="",
        type="application",
        homepage="https://github.com/Special-Week/",
        supported_adapters={"~onebot.v11"},
        extra={
            "author": "Special-Week",
            "link": "https://github.com/Special-Week/n",
            "version": "0.0.114514",
        },
    )

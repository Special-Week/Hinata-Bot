import time
import httpx
import jinja2
import random
import pkgutil
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_htmlrender import html_to_pic

from .diff import diff_text

env = jinja2.Environment(enable_async=True)
article_data = pkgutil.get_data(__name__, "templates/article.html").decode()
article_tpl = env.from_string(article_data)


async def check_text(text: str) -> Message:
    try:
        url = 'https://asoulcnki.asia/v1/api/check'
        async with httpx.AsyncClient() as client:
            resp = await client.post(url=url, json={'text': text})
            result = resp.json()

        if result['code'] != 0:
            return None

        data = result['data']
        if not data['related']:
            return '没有找到重复的小作文捏'

        rate = data['rate']
        related = data['related'][0]
        reply_url = str(related['reply_url']).strip()
        reply = related['reply']

        image = await render_reply(reply, diff=text)
        if not image:
            return None

        msg = Message()
        msg.append('总复制比 {:.2f}%'.format(rate * 100))
        msg.append(MessageSegment.image(image))
        msg.append(f'链接：{reply_url}')
        return msg
    except Exception as e:
        logger.warning(f"Error in check_text: {e}")
        return None


async def random_text(keyword: str = "") -> Message:
    try:
        url = 'https://asoulcnki.asia/v1/api/ranking'
        params = {
            'pageSize': 10,
            'pageNum': 1,
            'timeRangeMode': 0,
            'sortMode': 0
        }
        if keyword:
            params['keywords'] = keyword
        else:
            params['pageNum'] = random.randint(1, 100)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url=url, params=params)
            result = resp.json()

        if result['code'] != 0:
            return None

        replies = result['data']['replies']
        if not replies:
            return '没有找到小作文捏'

        reply = random.choice(replies)
        image = await render_reply(reply)
        if not image:
            return None

        reply_url = f"https://t.bilibili.com/{reply['dynamic_id']}/#reply{reply['rpid']}"
        msg = Message()
        msg.append(MessageSegment.image(image))
        msg.append(f'链接：{reply_url}')
        return msg
    except Exception as e:
        logger.warning(f"Error in random_text: {e}")
        return None


async def render_reply(reply: dict, diff: str = "") -> bytes:
    try:
        article = {}
        article['username'] = reply['m_name']
        article['like'] = reply['like_num']
        article['all_like'] = reply['similar_like_sum']
        article['quote'] = reply['similar_count']
        article['text'] = diff_text(
            diff, reply['content']) if diff else reply['content']
        article['time'] = time.strftime(
            "%Y-%m-%d", time.localtime(reply['ctime']))

        html = await article_tpl.render_async(article=article)
        return await html_to_pic(html, wait=0, viewport={"width": 500, "height": 100})
    except Exception as e:
        logger.warning(f"Error in render_reply: {e}")
        return None

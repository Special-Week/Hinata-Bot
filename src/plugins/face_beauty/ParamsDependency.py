from typing import Dict, Any, Type, Optional

from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event


# NoneBot2-ClassDependencyInjection-UserBasicInfo
class User:
    def __init__(self, event_type: Type[Event]):
        self.event_type = event_type

    async def __call__(self, bot: Bot, event: Event, matcher: Matcher) -> Optional[Dict[str, Any]]:
        if not isinstance(event, self.event_type):
            await matcher.skip()
        self.user_id = event.get_user_id()
        try:
            self.session_id = event.get_session_id()
            self.group_id = self.session_id.split('_')[1]
        except (ValueError, IndexError):
            self.group_id = None
        user_info = await bot.get_stranger_info(user_id=int(self.user_id))

        user = {'user_id': self.user_id,
                'group_id': self.group_id,
                'session_id': self.session_id,
                'nickname': user_info['nickname'],
                'sex': user_info['sex'],
                'age': user_info['age'],
                'level': user_info['level'],
                'login_days': user_info['login_days']
                }
        return user


# NoneBot2-ClassDependencyInjection-GroupUserBasicInfo
class GroupUser(User):
    async def __call__(self, bot: Bot, event: Event, matcher: Matcher) -> Optional[Dict[str, Any]]:
        user = await super().__call__(bot=bot, event=event, matcher=matcher)
        if user['group_id'] is None:
            await matcher.skip()
        return user


# NoneBot2-ClassDependencyInjection-PrivateUserBasicInfo
class PrivateUser(User):
    async def __call__(self, bot: Bot, event: Event, matcher: Matcher) -> Optional[Dict[str, Any]]:
        user = await super().__call__(bot=bot, event=event, matcher=matcher)
        if user['group_id'] is not None:
            await matcher.skip()
        return user

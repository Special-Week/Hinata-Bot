import fractions
import math
import re
from typing import Any, List, Union

from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from scipy.interpolate import lagrange # type: ignore

from .utils import Nums


class HomoNumber:
    # 参考并移植自 https://github.com/itorr/homo
    # 参考并移植自 https://github.com/HiDolen/nonebot_plugin_homonumber
    async def main(self, matcher: Matcher, arg: Message = CommandArg()) -> None:
        number: str = arg.extract_plain_text()
        message: str = self.demolish(number)
        if not message:
            message = "需要一个数字，这事数字吗（恼）"
        await matcher.send(message)

    def demolish(self, num_str: str) -> str:
        if not re.sub("[-.]", "", num_str).isdigit():  # 如果输入的不是数字
            return ""
        num: Union[float, int] = float(num_str) if "." in num_str else int(num_str)
        if not math.isfinite(num):  # 若输入的不是 无穷 或 不是数字
            return f"这么臭的{num}有必要论证吗"

        if num < 0:
            return f"(11-4-5+1-4)*({self.demolish(str(num * -1))})"
        if not isinstance(num, int):  # 如果不是整数
            temp = str(num)
            start_on: int = temp.find(".") + 1
            length: int = len(temp[start_on:])
            _next: str = self.demolish(str(int(num * (10**length))))
            return f"({_next})/({self.demolish(str(10**length))})"

        if num in Nums:
            return Nums[num]
        div: int = next((one for one in Nums if num >= one), 1)  # 获取刚好比 num 大的那个数
        first_number: str = self.demolish(str(int(num / div)))
        second_number: str = self.demolish(str(int(num % div)))
        return f"({Nums[div]})*({first_number})+({second_number})"


class LagrangeInterpolation:
    async def main(self, matcher: Matcher, arg: Message = CommandArg()) -> None:
        msg: str = arg.extract_plain_text().strip()
        if not msg:
            return
        msgs: List[str] = msg.split(" ")
        items: List[str] = [item.strip() for item in msgs if item.strip()]
        if len(items) < 2 or not self.check_if_number(items):
            return
        y: List[Union[float, int]] = self.convert_to_number(items)      # y轴坐标
        x = list(range(1, len(y) + 1))  # x轴坐标
        coeffs: list = self.lagrange_fraction(x, y)
        func: str = ""
        count: int = len(coeffs)
        for i in coeffs:
            count -= 1
            if str(i) == "0":
                continue
            if count == 0:
                func += f"({str(i)})" if int(i) < 0 else str(i)
            elif count == 1:
                func += "x+" if str(i) == "1" else f"({str(i)})x+"
            else:
                func += f"x^{count}+" if str(i) == "1" else f"({str(i)})x^{count}+"
        func = func[:-1] if func[-1] == "+" else func
        await matcher.send(f"f(x) = {func}")

    @staticmethod
    def lagrange_fraction(x, y) -> list:
        """拉格朗日插值法，返回分数列表"""
        p: Any = lagrange(x, y)
        c: Any = p.c
        d: Any = p.order
        return [fractions.Fraction(c[i]).limit_denominator() for i in range(d + 1)]

    @staticmethod
    def check_if_number(strings: List[str]) -> bool:
        """用于判断列表的str是否为数字, 匹配正负整数和正负小数"""
        pattern = r"^[-+]?\d*\.?\d+$"
        flag = True
        # 但凡出现一个不匹配的就返回False
        return next(
            (False for string in strings if not re.match(pattern, string)), flag
        )

    @staticmethod
    def convert_to_number(strings: List[str]) -> List[Union[int, float]]:
        """将字符串列表转换为数字列表"""
        numbers: list = []
        for string in strings:
            if string.isdigit():    # 正整数直接插入
                numbers.append(int(string))
            elif string.startswith("-") and string[1:].isdigit():  # 判断是否为负整数
                numbers.append(int(string))
            else:       # 只剩下小数的可能了
                numbers.append(float(string))
        return numbers


homo_number = HomoNumber()
lagrange_interpolation = LagrangeInterpolation()

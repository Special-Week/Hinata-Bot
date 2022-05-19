from typing import List


class cache:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.start == other.start and self.end == other.end
        else:
            return False


def merge(intervals: List[cache]):
    """合并重复区间
    :param intervals: 待去重区间
    :returns: 去重的区间（根据开始位置逆序）
    """
    if len(intervals) == 0:
        return []
    intervals = sorted(intervals, key=lambda s: s.start)
    outputs = [intervals[0]]
    for s in intervals:
        last_interval = outputs[-1]
        if last_interval.end < s.start:
            outputs.append(s)
        else:
            last_interval.end = max(last_interval.end, s.end)
    return sorted(outputs, key=lambda s: s.start, reverse=True)


def compare(origin: str, dest: str, sensitive: int):
    """标记重复区间
    :param origin: 待查重文本
    :param dest: 返回的文本
    :param sensitive: 敏感长度
    :returns: 重复区间数组（根据开始位置逆序）
    """
    length = max(len(origin), len(dest)) ** 2
    matrix = [0 for i in range(length)]
    cache_array: List[cache] = []

    def convert(index_y: int, index_x: int):
        return index_y * len(origin) + index_x

    def remove(arr: List[cache], obj: cache):
        return list(filter(lambda s: s != obj, arr))

    def new_cache(end: int, offset: int):
        start = end - offset
        start = 0 if start < 0 else start + 1
        return cache(start, offset + start)

    for index, s in enumerate(origin):
        if dest[0] == s:
            matrix[index] = 1

    for index_x, x in enumerate(dest):
        for index_y, y in enumerate(origin):
            index = convert(index_y, index_x)
            pre_index = convert(index_y - 1, index_x - 1)
            if x == y:
                if index_y == 0:
                    matrix[index] = 1
                    continue
                matrix[index] = matrix[pre_index] + 1
                if matrix[index] >= sensitive:
                    cache_array.append(new_cache(index_y, matrix[index]))
                if matrix[index] > sensitive:
                    cache_array = remove(cache_array, new_cache(
                        index_y - 1, matrix[pre_index]))
    return merge(cache_array)


def render(s: str, flag: List[cache], tag: str):
    """给重复区间加tag
    :param s: raw text
    :param flag: repeat area Array
    :param tag: used tag, default em
    :returns: tagged text
    """
    arr = list(s)
    for i in flag:
        arr.insert(i.end, f'</{tag}>')
        arr.insert(i.start, f'<{tag}>')
    return ''.join(arr)


def diff_text(origin: str, dest: str, sensitive=4, tag='strong'):
    """对文本重复对比，给重复部分加tag
    :param origin: 待查重文本
    :param dest: 服务器返回的文本
    :param sensitive: 敏感长度
    :param tag: HTML tag, example a, em
    :returns: 做好标记的文本
    """
    flag = compare(dest, origin, sensitive)
    return render(dest, flag, tag)

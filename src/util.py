import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from colorama import Fore

disclaimer_text = """
本站内容由人工智能大语言模型生成。其内容用于技术演示，不构成任何投资建议，也不作为任何法律法规、监管政策的依据。用户不应采用以上信息作为投资决策依据或依赖该等信息做出法律行为，由此造成的一切后果由用户自行承担。
"""


def remove_leading_spaces(s: str) -> str:
    """删除文本中的前导空格

    Args:
        s (str): 源字符串

    Returns:
        str: 处理之后的字符串
    """
    return '\n'.join([line.strip() for line in s.splitlines()])


def append_discliamer(md_text: str) -> str:
    """markdown 文本末尾增加免责声明

    Args:
        md_text (str): 源 markdown 文本

    Returns:
        str: 处理之后的 markdown 文本
    """    """"""

    output = f"""{md_text}

    {disclaimer_text}"""

    return remove_leading_spaces(output)


def in_trading_time(zone: str = 'Asia/Shanghai') -> bool:
    """判断是否在交易时间

    Args:
        zone (str): 时区

    Returns:
        bool: 是否在交易时间内
    """
    # 判断当前时间是否在指定范围内
    ny_tz = ZoneInfo(zone)
    now_ny = datetime.now(ny_tz)
    market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)

    # 检查是否在交易日
    if now_ny.weekday() in range(0, 5):  # 0-4 表示周一到周五
        return market_open <= now_ny <= market_close
    return False


def identify_stock_type(code: str) -> str:
    """根据代码判断市场类型

    Args:
        code (str): 证券代码

    Returns:
        str: 市场类型
    """
    # 处理代码可能存在的前后空格
    code = str(code).strip()
    # 判断是否为 A 股
    if code.isdigit() and len(code) == 6:
        if code.startswith(('60', '688', '00', '30', '8', '9')):
            return 'A股'
    # 判断是否为 A 股 ETF
    if code.isdigit() and len(code) == 6:
        if code.startswith(('5', '15')):
            return 'A股ETF'
    # 判断是否为港股
    if code.isdigit() and len(code) == 5:
        return '港股'
    return '未知类型'


def nowstr(tz='Asia/Shanghai') -> str:
    """获得当前时间字符串

    Returns:
        _type_: 输出"%Y-%m-%d %H:%M:%S"格式的当前时间字符串
    """
    now = datetime.now(ZoneInfo(tz))
    return now.strftime("%Y-%m-%d %H:%M:%S")


def todaystr() -> str:
    """获得当前日期字符串

    Returns:
        _type_: 输出"%Y-%m-%d"格式的当前日期字符串
    """
    now = datetime.now()
    return now.strftime("%Y%m%d")


def send_voice(message: str) -> int:
    """采用苹果默认的say命令播报语音

    Args:
        message (str): _description_

    Returns:
        int: _description_
    """
    command = f'''say {message}'''
    return subprocess.call(command, shell=True)


def numbers_in_chinese(text: str) -> str:
    """
    将字符串中的阿拉伯数字替换为中文数字
    """
    chinese_digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    result = []
    for char in text:
        if char.isdigit():
            num = int(char)
            result.append(chinese_digits[num])
        else:
            result.append(char)
    return ''.join(result)


def add_spaces_in_str(text: str) -> str:
    """
    在字符串中每隔指定数量的字符添加一个空格
    """
    return ' '.join(text[i:i+1] for i in range(0, len(text), 1))


def is_workday() -> bool:
    """判断是否工作日

    Returns:
        bool: _description_
    """
    today = datetime.now().weekday()
    return today < 5  # 0-4 代表周一至周五


def is_weekend() -> bool:
    """判断是否周末

    Returns:
        bool: _description_
    """
    today = datetime.now().weekday()
    return today > 4  # 0-4 代表周一至周五


def this_year_str() -> str:
    """返回当年字符串

    Returns:
        str: _description_
    """
    return todaystr()[:4]


def format_for_term(order: str) -> str:
    """格式化指令在终端输出"""
    if order == '买入':
        return f'{Fore.RED}买入{Fore.RESET}'
    elif order == '卖出':
        return f'{Fore.GREEN}卖出{Fore.RESET}'
    else:
        return f'{Fore.BLUE}观望{Fore.RESET}'


def format_for_markdown(order: str) -> str:
    """格式化指令以markdown输出"""
    if order == '买入':
        return ':red[买入]'
    elif order == '卖出':
        return ':green[卖出]'
    else:
        return ':blue[观望]'

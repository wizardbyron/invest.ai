from datetime import datetime
from zoneinfo import ZoneInfo
from enum import StrEnum


class StockType(StrEnum):
    A = "A股"
    A_ETF = "A股ETF"
    HK = "港股"
    US = "美股"


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

    ## 免责声明
    
    以上内容由人工智能大语言模型生成，并用于研究实验目的。
    其内容不构成任何投资建议，也不作为任何法律法规、监管政策的依据。
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。
    """

    return remove_leading_spaces(output)


def is_trading_time(zone: str) -> bool:
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
        if code.startswith(('60', '688', '00', '30')):
            return 'A股'
    # 判断是否为 A 股 ETF
    if code.isdigit() and len(code) == 6:
        if code.startswith(('51', '15', '16', '18')):
            return 'A股ETF'
    # 判断是否为港股
    if code.isdigit() and len(code) == 5:
        return '港股'
    return '未知类型'

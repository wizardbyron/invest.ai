import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv
from futu import RET_OK, OpenQuoteContext, AuType, KLType
from pandas import DataFrame

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.util import identify_stock_type, futu_symbol

load_dotenv()


class FutuAPI:
    """Futu Open API 技能

    通过富途开放平台获取股票行情数据，支持自动识别不同市场（A股、港股、美股）的股票代码。
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11111):
        """初始化Futu API连接

        Args:
            host: OpenD服务地址，默认为本地127.0.0.1
            port: OpenD服务端口，默认为11111
        """
        self.host = host
        self.port = port
        self.quote_ctx = None

    def _get_quote_ctx(self) -> OpenQuoteContext:
        """获取行情上下文连接"""
        if self.quote_ctx is None:
            self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
        return self.quote_ctx

    def _close(self):
        """关闭行情连接"""
        if self.quote_ctx:
            self.quote_ctx.close()
            self.quote_ctx = None

    @staticmethod
    def _period_to_kltype(period: str) -> KLType:
        """转换周期为KLType

        Args:
            period: K线周期：daily/weekly/monthly

        Returns:
            KLType: 对应的KLType枚举值
        """
        if period == "daily":
            return KLType.K_DAY
        elif period == "weekly":
            return KLType.K_WEEK
        elif period == "monthly":
            return KLType.K_MON
        else:
            raise ValueError(f"不支持的周期: {period}")

    @staticmethod
    def _adjust_flag_to_autype(adjust_flag: str) -> AuType:
        """转换复权类型

        Args:
            adjust_flag: 复权标志：qfq(前复权)/hfq(后复权)

        Returns:
            AuType: 对应的AuType枚举值
        """
        if adjust_flag == "qfq":
            return AuType.QFQ
        elif adjust_flag == "hfq":
            return AuType.HFQ
        else:
            raise ValueError(f"不支持的复权类型: {adjust_flag}")

    def identify_market(self, symbol: str) -> str:
        """自动识别股票代码所属市场

        Args:
            symbol: 股票代码

        Returns:
            str: 市场类型（A股/A股ETF/港股/美股/未知类型）
        """
        return identify_stock_type(symbol)

    def format_futu_code(self, symbol: str) -> str:
        """将股票代码格式化为Futu格式（市场.代码）

        Args:
            symbol: 股票代码

        Returns:
            str: Futu格式的代码，如 HK.00700
        """
        return futu_symbol(symbol)

    def get_klines(
        self,
        symbol: str,
        period: str = "daily",
        start_date: str = None,
        end_date: str = None,
        adjust_flag: str = "qfq",
    ) -> DataFrame:
        """获取历史K线数据

        自动识别股票代码所属市场，并从Futu API获取K线数据。

        Args:
            symbol: 股票代码，支持A股（6位数字）、港股（5位数字）、美股（字母代码）
            period: K线周期，可选：daily/weekly/monthly，默认为daily
            start_date: 开始日期，格式：YYYY-MM-DD，默认为一年前
            end_date: 结束日期，格式：YYYY-MM-DD，默认为今天
            adjust_flag: 复权类型，可选：qfq(前复权)/hfq(后复权)，默认为qfq

        Returns:
            DataFrame: 包含K线数据的DataFrame

        Raises:
            ValueError: 当参数无效或获取数据失败时
        """
        # 设置默认日期
        if end_date is None:
            end_date = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
        if start_date is None:
            from datetime import timedelta

            start_date = (
                datetime.now(ZoneInfo("Asia/Shanghai")) - timedelta(days=365)
            ).strftime("%Y-%m-%d")

        # 识别市场类型
        market_type = self.identify_market(symbol)
        if market_type == "未知类型":
            raise ValueError(f"无法识别股票代码 {symbol} 的市场类型")

        # 转换代码格式
        futu_code = self.format_futu_code(symbol)

        # 转换周期和复权类型
        kl_type = self._period_to_kltype(period)
        au_type = self._adjust_flag_to_autype(adjust_flag)

        quote_ctx = self._get_quote_ctx()
        page_size = 1000
        all_data = pd.DataFrame()

        try:
            # 请求第一页数据
            ret, data, page_req_key = quote_ctx.request_history_kline(
                code=futu_code,
                start=start_date,
                end=end_date,
                autype=au_type,
                ktype=kl_type,
                max_count=page_size,
            )

            if ret != RET_OK:
                raise ValueError(f"获取数据失败: {data}")

            all_data = data

            # 请求后续页面数据
            while page_req_key is not None:
                ret, data, page_req_key = quote_ctx.request_history_kline(
                    code=futu_code,
                    start=start_date,
                    end=end_date,
                    autype=au_type,
                    ktype=kl_type,
                    max_count=page_size,
                    page_req_key=page_req_key,
                )

                if ret != RET_OK:
                    raise ValueError(f"获取分页数据失败: {data}")

                all_data = pd.concat([all_data, data], ignore_index=True)

            if all_data.empty:
                raise ValueError("未获取到数据，请检查参数是否正确")

            # 重命名列以符合项目规范
            all_data.rename(
                columns={
                    "code": "股票代码",
                    "name": "股票名称",
                    "time_key": "日期",
                    "open": "开盘",
                    "close": "收盘",
                    "high": "最高",
                    "low": "最低",
                    "volume": "成交量",
                    "turnover": "成交额",
                    "turnover_rate": "换手率",
                    "pe_ratio": "市盈率",
                    "change_rate": "涨跌幅",
                    "last_close": "昨收",
                },
                inplace=True,
            )

            # 处理日期格式
            all_data["日期"] = all_data["日期"].str.replace(" 00:00:00", "")

            # 计算涨跌额
            all_data["涨跌额"] = all_data["收盘"] - all_data["开盘"]

            return all_data

        except Exception as e:
            raise ValueError(f"获取K线数据失败: {str(e)}")

        finally:
            self._close()

    def get_snapshot(self, symbol: str) -> dict:
        """获取股票实时快照

        Args:
            symbol: 股票代码

        Returns:
            dict: 包含股票实时信息的字典
        """
        futu_code = self.format_futu_code(symbol)
        quote_ctx = self._get_quote_ctx()

        try:
            ret, data = quote_ctx.get_market_snapshot([futu_code])

            if ret != RET_OK:
                raise ValueError(f"获取快照失败: {data}")

            if data.empty:
                raise ValueError(f"未找到股票 {symbol} 的快照数据")

            # 转换为字典格式
            result = data.to_dict("records")[0]
            return result

        except Exception as e:
            raise ValueError(f"获取快照失败: {str(e)}")

        finally:
            self._close()


# 便捷函数：直接获取K线数据
def get_klines(
    symbol: str,
    period: str = "daily",
    start_date: str = None,
    end_date: str = None,
    adjust_flag: str = "qfq",
    host: str = "127.0.0.1",
    port: int = 11111,
) -> DataFrame:
    """便捷函数：从Futu API获取历史K线数据

    自动识别股票代码所属市场，支持A股、港股、美股。

    Args:
        symbol: 股票代码
        period: K线周期：daily/weekly/monthly
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        adjust_flag: 复权类型：qfq/hfq
        host: OpenD服务地址
        port: OpenD服务端口

    Returns:
        DataFrame: K线数据
    """
    api = FutuAPI(host=host, port=port)
    return api.get_klines(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust_flag=adjust_flag,
    )


# 便捷函数：识别市场类型
def identify_market(symbol: str) -> str:
    """便捷函数：识别股票代码所属市场

    Args:
        symbol: 股票代码

    Returns:
        str: 市场类型
    """
    return identify_stock_type(symbol)


# 便捷函数：格式化代码
def format_futu_code(symbol: str) -> str:
    """便捷函数：将股票代码格式化为Futu格式

    Args:
        symbol: 股票代码

    Returns:
        str: Futu格式代码
    """
    return futu_symbol(symbol)


if __name__ == "__main__":
    # 测试示例
    print("=== Futu API Skill 测试 ===")

    # 测试市场识别
    test_codes = ["00700", "000001", "AAPL", "600000", "510500"]
    for code in test_codes:
        market = identify_market(code)
        futu_fmt = format_futu_code(code)
        print(f"代码: {code:10s} -> 市场: {market:8s} -> Futu格式: {futu_fmt}")

    # 测试获取K线数据（需要先启动OpenD服务）
    try:
        print("\n=== 测试获取K线数据 ===")
        df = get_klines(
            symbol="00700",
            period="daily",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        print(f"获取到 {len(df)} 条数据")
        print(df.head())
    except Exception as e:
        print(f"获取数据失败（请确保OpenD服务已启动）: {e}")

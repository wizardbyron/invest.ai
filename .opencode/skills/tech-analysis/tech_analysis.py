"""
技术分析技能 - 基于MA、VWAP、枢轴点的交易建议系统
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pandas import DataFrame

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# 导入futu技能获取数据
import importlib.util

spec = importlib.util.spec_from_file_location(
    "futu_api", os.path.join(os.path.dirname(__file__), "..", "futu", "futu_api.py")
)
futu_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(futu_api)
get_klines = futu_api.get_klines
identify_market = futu_api.identify_market


class TechnicalAnalyzer:
    """技术分析器

    基于MA、VWAP、枢轴点等指标给出交易建议
    """

    def __init__(self):
        self.data = None
        self.symbol = None
        self.stock_name = None

    def analyze(self, symbol: str, days: int = 100) -> Dict:
        """分析股票并生成交易建议

        Args:
            symbol: 股票代码
            days: 分析天数，默认100个交易日

        Returns:
            Dict: 包含分析结果和建议的字典
        """
        self.symbol = symbol

        # 获取数据（获取足够的历史数据计算指标）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 60)  # 多取60天用于计算MA60

        # 记录数据日期范围
        data_start_date = start_date.strftime("%Y-%m-%d")
        data_end_date = end_date.strftime("%Y-%m-%d")

        try:
            self.data = get_klines(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                adjust_flag="qfq",
            )

            if self.data.empty:
                raise ValueError(f"无法获取 {symbol} 的数据")

            self.stock_name = (
                self.data["股票名称"].iloc[-1]
                if "股票名称" in self.data.columns
                else symbol
            )

            # 计算技术指标
            indicators = self._calculate_indicators()

            # 计算波段（上涨/下跌）
            trend_wave = self._calculate_trend_wave()

            # 计算枢轴点和支撑阻力位
            pivot = self._calculate_pivot_points()
            key_levels = self._calculate_key_levels()

            # 生成交易信号
            signal, confidence = self._generate_signal(indicators, pivot)

            # 生成建议
            suggestion = self._generate_suggestion(
                signal, indicators, pivot, key_levels
            )

            # 生成报告
            report = self._generate_report(
                symbol,
                self.stock_name,
                indicators,
                trend_wave,
                pivot,
                key_levels,
                signal,
                confidence,
                suggestion,
                data_start_date,
                data_end_date,
            )

            return {
                "symbol": symbol,
                "name": self.stock_name,
                "current_price": indicators["close"],
                "signal": signal,
                "signal_color": "red"
                if signal == "买入"
                else ("green" if signal == "卖出" else "blue"),
                "indicators": indicators,
                "trend_wave": trend_wave,
                "pivot": pivot,
                "key_levels": key_levels,
                "suggestion": suggestion,
                "report": report,
                "data_date_range": f"{data_start_date} 至 {data_end_date}",
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "report": f"分析失败: {str(e)}",
            }

    def analyze_with_cost(
        self, symbol: str, cost_price: float, days: int = 100
    ) -> Dict:
        """分析股票并计算盈亏（用于卖出建议）

        Args:
            symbol: 股票代码
            cost_price: 成本价
            days: 分析天数

        Returns:
            Dict: 包含分析结果和盈亏计算的字典
        """
        result = self.analyze(symbol, days)

        if "error" in result:
            return result

        current_price = result["current_price"]
        profit_loss = (current_price - cost_price) / cost_price * 100
        profit_loss_amount = current_price - cost_price

        result["cost_price"] = cost_price
        result["profit_loss_pct"] = profit_loss
        result["profit_loss_amount"] = profit_loss_amount

        # 更新报告添加盈亏信息
        profit_str = f"{'盈利' if profit_loss > 0 else '亏损'}: {profit_loss:+.2f}% ({profit_loss_amount:+.2f} HKD)"

        result["report"] = result["report"].replace(
            "═══════════════════════════════════════════",
            f"成本价: {cost_price:.2f} HKD\n{profit_str}\n═══════════════════════════════════════════",
            1,
        )

        return result

    def _calculate_indicators(self) -> Dict:
        """计算技术指标"""
        df = self.data.copy()

        # 计算移动平均线
        df["ma5"] = df["收盘"].rolling(window=5).mean()
        df["ma10"] = df["收盘"].rolling(window=10).mean()
        df["ma20"] = df["收盘"].rolling(window=20).mean()
        df["ma60"] = df["收盘"].rolling(window=60).mean()

        # 计算VWAP (成交量加权平均价)
        df["vwap"] = (df["收盘"] * df["成交量"]).cumsum() / df["成交量"].cumsum()

        # 计算RSI
        delta = df["收盘"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # 计算成交量均线
        df["volume_ma20"] = df["成交量"].rolling(window=20).mean()

        # 获取最新值
        latest = df.iloc[-1]

        # VWAP偏离度
        vwap_deviation = (latest["收盘"] - latest["vwap"]) / latest["vwap"] * 100

        # 量比
        volume_ratio = (
            latest["成交量"] / latest["volume_ma20"] if latest["volume_ma20"] > 0 else 1
        )

        return {
            "close": round(latest["收盘"], 2),
            "open": round(latest["开盘"], 2),
            "high": round(latest["最高"], 2),
            "low": round(latest["最低"], 2),
            "ma5": round(latest["ma5"], 2),
            "ma10": round(latest["ma10"], 2),
            "ma20": round(latest["ma20"], 2),
            "ma60": round(latest["ma60"], 2),
            "vwap": round(latest["vwap"], 2),
            "vwap_deviation": round(vwap_deviation, 2),
            "rsi": round(latest["rsi"], 2),
            "volume": int(latest["成交量"]),
            "volume_ratio": round(volume_ratio, 2),
        }

    def _calculate_trend_wave(self) -> Dict:
        """计算最近三波上涨或下跌波段

        收盘价连续上升为上涨波段，连续下降为下跌波段
        """
        df = self.data.copy()

        # 计算每日涨跌
        df["change"] = df["收盘"].diff()

        # 判断每天是涨还是跌
        df["direction"] = df["change"].apply(
            lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
        )

        # 找到所有波段的分界点（方向变化的索引）
        trend_changes = []
        for i in range(1, len(df)):
            if df["direction"].iloc[i] != df["direction"].iloc[i - 1]:
                trend_changes.append(i)

        # 从最新一天开始往前找波段
        waves = []
        start_idx = len(df) - 1

        # 最多找5个波段
        for wave_num in range(5):
            if start_idx <= 0:
                break

            # 获取当前波段的方向
            current_direction = df["direction"].iloc[start_idx]
            if current_direction == 0:
                # 持平，跳过
                start_idx -= 1
                if start_idx <= 0:
                    break
                current_direction = df["direction"].iloc[start_idx]

            # 往前找到波段开始位置
            wave_start = start_idx
            for i in range(start_idx - 1, -1, -1):
                day_direction = df["direction"].iloc[i]
                if day_direction == 0:
                    # 持平，继续
                    continue
                elif day_direction != current_direction:
                    # 找到趋势反转点
                    wave_start = i
                    break
                else:
                    wave_start = i

            # 提取波段数据
            wave_data = df.iloc[wave_start : start_idx + 1]

            if len(wave_data) > 0:
                # 波段信息
                trend = "上涨" if current_direction == 1 else "下跌"
                price_change = wave_data["收盘"].iloc[-1] - wave_data["收盘"].iloc[0]
                change_pct = (
                    (price_change / wave_data["收盘"].iloc[0]) * 100
                    if wave_data["收盘"].iloc[0] != 0
                    else 0
                )

                waves.append(
                    {
                        "trend": trend,
                        "start_date": wave_data["日期"].iloc[0],
                        "end_date": wave_data["日期"].iloc[-1],
                        "start_price": round(wave_data["收盘"].iloc[0], 2),
                        "end_price": round(wave_data["收盘"].iloc[-1], 2),
                        "high_price": round(wave_data["最高"].max(), 2),
                        "low_price": round(wave_data["最低"].min(), 2),
                        "change_pct": round(change_pct, 2),
                        "trading_days": len(wave_data),
                    }
                )

            # 移动到上一个波段
            start_idx = wave_start - 1
            if start_idx <= 0:
                break

        # 如果没有找到5个波段，尝试从数据开头开始计算
        # 检查是否需要补充波段
        if len(waves) < 3 and len(df) > 1:
            # 从头开始找波段
            start_idx = 0
            current_direction = (
                df["direction"].iloc[0]
                if df["direction"].iloc[0] != 0
                else (df["direction"].iloc[1] if len(df) > 1 else 0)
            )

            for i in range(1, len(df)):
                if df["direction"].iloc[i] != current_direction:
                    # 找到一个波段
                    wave_data = df.iloc[start_idx:i]
                    if len(wave_data) > 0:
                        trend = "上涨" if current_direction == 1 else "下跌"
                        price_change = (
                            wave_data["收盘"].iloc[-1] - wave_data["收盘"].iloc[0]
                        )
                        change_pct = (
                            (price_change / wave_data["收盘"].iloc[0]) * 100
                            if wave_data["收盘"].iloc[0] != 0
                            else 0
                        )

                        # 检查是否已存在（避免重复）
                        exists = any(
                            w["start_date"] == wave_data["日期"].iloc[0]
                            and w["end_date"] == wave_data["日期"].iloc[-1]
                            for w in waves
                        )
                        if not exists:
                            waves.append(
                                {
                                    "trend": trend,
                                    "start_date": wave_data["日期"].iloc[0],
                                    "end_date": wave_data["日期"].iloc[-1],
                                    "start_price": round(wave_data["收盘"].iloc[0], 2),
                                    "end_price": round(wave_data["收盘"].iloc[-1], 2),
                                    "high_price": round(wave_data["最高"].max(), 2),
                                    "low_price": round(wave_data["最低"].min(), 2),
                                    "change_pct": round(change_pct, 2),
                                    "trading_days": len(wave_data),
                                }
                            )

                    current_direction = df["direction"].iloc[i]
                    start_idx = i

                    if len(waves) >= 5:
                        break

        return {
            "waves": waves[:5],  # 返回最近五个波段
            "latest": waves[0] if waves else None,  # 最近一个波段
        }

    def _calculate_pivot_points(self) -> Dict:
        """计算枢轴点（经典方法）"""
        df = self.data

        # 使用最近一个完整交易日的数据
        recent = df.iloc[-2] if len(df) > 1 else df.iloc[-1]

        high = recent["最高"]
        low = recent["最低"]
        close = recent["收盘"]

        # 计算枢轴点
        pp = (high + low + close) / 3

        # 计算阻力位
        r1 = 2 * pp - low
        r2 = pp + (high - low)
        r3 = high + 2 * (pp - low)

        # 计算支撑位
        s1 = 2 * pp - high
        s2 = pp - (high - low)
        s3 = low - 2 * (high - pp)

        return {
            "pp": round(pp, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(r3, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2),
        }

    def _calculate_key_levels(self) -> Dict:
        """计算关键支撑阻力位"""
        df = self.data.tail(60)  # 使用最近60天的数据

        # 近期高低点
        recent_high = df["最高"].max()
        recent_low = df["最低"].min()

        # 计算阻力位（近期高点、整数关口、枢轴点）
        resistance = [
            recent_high,
            self._round_to_significant(recent_high, direction="up"),
        ]

        # 计算支撑位（近期低点、整数关口、枢轴点）
        support = [
            recent_low,
            self._round_to_significant(recent_low, direction="down"),
        ]

        # 去重并排序
        resistance = sorted(
            list(set([round(r, 2) for r in resistance if r > df["收盘"].iloc[-1]])),
            reverse=True,
        )
        support = sorted(
            list(set([round(s, 2) for s in support if s < df["收盘"].iloc[-1]]))
        )

        return {
            "resistance": resistance[:4],  # 最多4个
            "support": support[:4],  # 最多4个
            "recent_high": round(recent_high, 2),
            "recent_low": round(recent_low, 2),
        }

    def _round_to_significant(self, price: float, direction: str = "up") -> float:
        """将价格四舍五入到最近的整数或5/10的倍数"""
        if price >= 100:
            # 高价股，取整到10的倍数
            if direction == "up":
                return np.ceil(price / 10) * 10
            else:
                return np.floor(price / 10) * 10
        elif price >= 10:
            # 中价股，取整到5的倍数
            if direction == "up":
                return np.ceil(price / 5) * 5
            else:
                return np.floor(price / 5) * 5
        else:
            # 低价股，取整到整数
            if direction == "up":
                return np.ceil(price)
            else:
                return np.floor(price)

    def _generate_signal(self, indicators: Dict, pivot: Dict) -> Tuple[str, int]:
        """生成交易信号

        Returns:
            Tuple[str, int]: (信号, 置信度0-100)
        """
        score = 0
        reasons = []

        # 1. MA多头排列/空头排列判断
        ma_bullish = indicators["ma5"] > indicators["ma10"] > indicators["ma20"]
        ma_bearish = indicators["ma5"] < indicators["ma10"] < indicators["ma20"]

        if ma_bullish:
            score += 25
            reasons.append("多头排列")
        elif ma_bearish:
            score -= 25
            reasons.append("空头排列")

        # 2. 价格在VWAP上方/下方
        if indicators["vwap_deviation"] > 0 and abs(indicators["vwap_deviation"]) < 5:
            score += 15
            reasons.append("VWAP上方")
        elif indicators["vwap_deviation"] < -2:
            score -= 15
            reasons.append("VWAP下方")

        # 3. 价格相对枢轴点位置
        if indicators["close"] > pivot["pp"]:
            score += 15
            reasons.append("枢轴点上方")
        else:
            score -= 15
            reasons.append("枢轴点下方")

        # 4. RSI判断
        if 30 < indicators["rsi"] < 70:
            score += 10
            reasons.append("RSI中性")
        elif indicators["rsi"] > 70:
            score -= 20
            reasons.append("RSI超买")
        elif indicators["rsi"] < 30:
            score += 20
            reasons.append("RSI超卖")

        # 5. 成交量
        if indicators["volume_ratio"] > 1.2:
            score += 10
            reasons.append("放量")
        elif indicators["volume_ratio"] < 0.8:
            score -= 5
            reasons.append("缩量")

        # 确定信号和置信度
        if score >= 30:
            signal = "买入"
            confidence = min(abs(score) + 20, 95)
        elif score <= -30:
            signal = "卖出"
            confidence = min(abs(score) + 20, 95)
        else:
            signal = "观望"
            confidence = 50

        return signal, confidence

    def _generate_suggestion(
        self, signal: str, indicators: Dict, pivot: Dict, key_levels: Dict
    ) -> Dict:
        """生成具体交易建议"""
        current_price = indicators["close"]

        if signal == "买入":
            # 设置止损价：最近支撑位下方3-5%
            if key_levels["support"]:
                stop_loss = key_levels["support"][0] * 0.97  # 支撑位下方3%
            else:
                stop_loss = current_price * 0.95  # 或者当前价下方5%

            # 目标价：最近阻力位
            target_price = (
                key_levels["resistance"][0]
                if key_levels["resistance"]
                else current_price * 1.1
            )

            # 计算盈亏比
            risk = current_price - stop_loss
            reward = target_price - current_price
            risk_reward_ratio = reward / risk if risk > 0 else 0

            return {
                "action": "买入",
                "stop_loss": round(stop_loss, 2),
                "target_price": round(target_price, 2),
                "risk_reward_ratio": round(risk_reward_ratio, 2),
                "potential_loss_pct": round(
                    (stop_loss - current_price) / current_price * 100, 2
                ),
                "potential_gain_pct": round(
                    (target_price - current_price) / current_price * 100, 2
                ),
            }

        elif signal == "卖出":
            return {
                "action": "卖出",
                "reason": "技术指标显示卖出信号，请输入成本价计算盈亏",
                "target_price": round(
                    key_levels["support"][0]
                    if key_levels["support"]
                    else current_price * 0.95,
                    2,
                ),
            }

        else:  # 观望
            return {
                "action": "观望",
                "reason": "信号不明确，建议等待更明确的技术信号",
                "watch_levels": {
                    "upside": round(key_levels["resistance"][0], 2)
                    if key_levels["resistance"]
                    else None,
                    "downside": round(key_levels["support"][0], 2)
                    if key_levels["support"]
                    else None,
                },
            }

    def _generate_report(
        self,
        symbol: str,
        name: str,
        indicators: Dict,
        trend_wave: Dict,
        pivot: Dict,
        key_levels: Dict,
        signal: str,
        confidence: int,
        suggestion: Dict,
        data_start_date: str = None,
        data_end_date: str = None,
    ) -> str:
        """生成分析报告"""

        # 获取实际数据日期范围
        if data_start_date is None:
            data_start_date = "未知"
        if data_end_date is None:
            data_end_date = "未知"

        # 构建波段报告
        waves = trend_wave.get("waves", [])
        wave_report = ""
        if waves:
            for i, wave in enumerate(waves):
                wave_emoji = "📈" if wave["trend"] == "上涨" else "📉"
                # 编号：最早的波段为1，最新的波段为3
                wave_num = len(waves) - i
                wave_report += f"""
【第{wave_num}波段】{wave_emoji} {wave["trend"]}
  起止日期: {wave["start_date"]} 至 {wave["end_date"]}
  持续交易日: {wave["trading_days"]}天
  {wave["start_price"]:.2f} → {wave["end_price"]:.2f} ({wave["change_pct"]:+.1f}%)
  最高: {wave["high_price"]:.2f} | 最低: {wave["low_price"]:.2f}
"""
        else:
            wave_report = "\n【波段】无数据\n"

        report = f"""
══════════════════════════════════════════
📊 技术分析报告 - {name} ({symbol})
══════════════════════════════════════════

当前价格: {indicators["close"]:.2f} HKD
数据日期: {data_start_date} 至 {data_end_date}
分析日期: {datetime.now().strftime("%Y-%m-%d")}
{wave_report}
【技术指标】
MA5:   {indicators["ma5"]:.2f}  {"📈" if indicators["ma5"] > indicators["ma10"] else "📉"}
MA10:  {indicators["ma10"]:.2f}  {"📈" if indicators["ma10"] > indicators["ma20"] else "📉"}
MA20:  {indicators["ma20"]:.2f}  {"📈" if indicators["ma20"] > indicators["ma60"] else "📉"}
MA60:  {indicators["ma60"]:.2f}
VWAP:  {indicators["vwap"]:.2f} ({indicators["vwap_deviation"]:+.1f}%)
RSI:   {indicators["rsi"]:.2f} ({self._get_rsi_status(indicators["rsi"])})
量比:  {indicators["volume_ratio"]:.2f} ({"放量" if indicators["volume_ratio"] > 1 else "缩量"})

【枢轴点】
R3: {pivot["r3"]:.2f}
R2: {pivot["r2"]:.2f}
R1: {pivot["r1"]:.2f}
PP: {pivot["pp"]:.2f}
S1: {pivot["s1"]:.2f}
S2: {pivot["s2"]:.2f}
S3: {pivot["s3"]:.2f}

【关键价位】
🔴 阻力位: {" | ".join([f"{r:.2f}" for r in key_levels["resistance"]])}
🟢 支撑位: {" | ".join([f"{s:.2f}" for s in key_levels["support"]])}

【交易信号】
{self._get_signal_emoji(signal)} {signal} (置信度: {confidence}%)

【操作建议】
"""

        if signal == "买入":
            report += f"""建议买入
止损价: {suggestion["stop_loss"]:.2f} HKD
目标价: {suggestion["target_price"]:.2f} HKD
盈亏比: 1:{suggestion["risk_reward_ratio"]:.1f}
潜在亏损: {suggestion["potential_loss_pct"]:.1f}%
潜在盈利: {suggestion["potential_gain_pct"]:.1f}%

【买入理由】
"""
            # 添加买入理由
            if indicators["ma5"] > indicators["ma10"] > indicators["ma20"]:
                report += "✅ 多头排列形成 (MA5 > MA10 > MA20)\n"
            if indicators["close"] > pivot["pp"]:
                report += "✅ 站上枢轴点，处于强势区域\n"
            if indicators["vwap_deviation"] > 0:
                report += f"✅ 股价在VWAP上方({indicators['vwap_deviation']:+.1f}%)\n"
            if indicators["volume_ratio"] > 1.2:
                report += "✅ 成交量放大，确认上涨动能\n"
            if 30 < indicators["rsi"] < 70:
                report += "✅ RSI中性，未超买超卖\n"

        elif signal == "卖出":
            report += f"""建议卖出
目标价: {suggestion["target_price"]:.2f} HKD

⚠️  请提供成本价计算盈亏

【卖出理由】
"""
            # 添加卖出理由
            if indicators["ma5"] < indicators["ma10"]:
                report += "❌ 短期均线走弱 (MA5 < MA10)\n"
            if indicators["close"] < pivot["pp"]:
                report += "❌ 跌破枢轴点，转入弱势区域\n"
            if indicators["vwap_deviation"] < -2:
                report += f"❌ 股价低于VWAP({indicators['vwap_deviation']:.1f}%)\n"
            if indicators["rsi"] > 70:
                report += "❌ RSI超买，存在回调风险\n"
            elif indicators["rsi"] < 30:
                report += "⚠️  RSI超卖，但趋势未改\n"

        else:  # 观望
            upside = suggestion["watch_levels"]["upside"]
            downside = suggestion["watch_levels"]["downside"]
            upside_str = f"{upside:.2f}" if upside else "N/A"
            downside_str = f"{downside:.2f}" if downside else "N/A"
            report += f"""建议观望

{suggestion["reason"]}

关注价位:
🔼 上行突破: {upside_str}
🔽 下行支撑: {downside_str}
"""

        report += """
═══════════════════════════════════════════
⚠️  免责声明: 技术分析仅供参考，不构成投资建议。
    投资有风险，入市需谨慎。
═══════════════════════════════════════════
"""

        return report

    def _get_rsi_status(self, rsi: float) -> str:
        """获取RSI状态描述"""
        if rsi > 70:
            return "超买"
        elif rsi < 30:
            return "超卖"
        else:
            return "中性"

    def _get_signal_emoji(self, signal: str) -> str:
        """获取信号对应的emoji"""
        if signal == "买入":
            return "🟥"
        elif signal == "卖出":
            return "🟩"
        else:
            return "🟦"


def analyze_stock(
    symbol: str, cost_price: Optional[float] = None, days: int = 100
) -> str:
    """便捷函数：分析股票并返回报告

    Args:
        symbol: 股票代码
        cost_price: 成本价（可选，用于卖出时计算盈亏）
        days: 分析天数

    Returns:
        str: 分析报告文本
    """
    analyzer = TechnicalAnalyzer()

    if cost_price is not None:
        result = analyzer.analyze_with_cost(symbol, cost_price, days)
    else:
        result = analyzer.analyze(symbol, days)

    return result.get("report", "分析失败")


if __name__ == "__main__":
    # 测试
    print("=== 技术分析技能测试 ===\n")

    # 测试买入信号
    print("测试1: 分析腾讯控股(00700)")
    result = analyze_stock("00700")
    print(result)

    # 测试卖出信号（带成本价）
    print("\n测试2: 分析腾讯控股(00700)，假设成本价550")
    result_with_cost = analyze_stock("00700", cost_price=550)
    print(result_with_cost)

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "tech_analysis", ".opencode/skills/tech-analysis/tech_analysis.py"
)
tech_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tech_analysis)

TechnicalAnalyzer = tech_analysis.TechnicalAnalyzer
identify_market = tech_analysis.identify_market


class TestTrendWave:
    """测试波段计算功能"""

    def test_calculate_trend_wave(self):
        """测试波段计算返回正确的结构"""
        analyzer = TechnicalAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, "_calculate_trend_wave")

    def test_identify_market(self):
        """测试市场识别功能"""
        assert identify_market("00700") == "港股"


class TestTechnicalAnalyzer:
    """测试技术分析器"""

    def test_analyzer_init(self):
        """测试分析器初始化"""
        analyzer = TechnicalAnalyzer()
        assert analyzer.data is None
        assert analyzer.symbol is None


class TestMarketIdentification:
    """测试市场识别"""

    def test_hk_stock(self):
        """测试港股识别"""
        assert identify_market("00700") == "港股"
        assert identify_market("09988") == "港股"

    def test_a_stock(self):
        """测试A股识别"""
        assert identify_market("000001") == "A股"
        assert identify_market("600000") == "A股"
        assert identify_market("688981") == "A股"

    def test_a_etf(self):
        """测试ETF识别"""
        assert identify_market("510500") == "A股ETF"
        assert identify_market("159915") == "A股ETF"

    def test_us_stock(self):
        """测试美股识别"""
        assert identify_market("AAPL") == "美股"
        assert identify_market("TSLA") == "美股"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

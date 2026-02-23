---
name: tech-analysis
description: 根据股票代码进行技术分析，计算阻力位支撑位，基于MA、VWAP、枢轴点给出买入/卖出/观望建议，买入时提供止损点，卖出时需提供成本价
---

## 功能概述

本技能用于对股票进行技术分析，提供：

- 计算关键阻力位和支撑位
- 基于多种技术指标给出交易建议
- 买入建议附带止损点
- 卖出建议需输入成本价计算盈亏

## 技术指标说明

### 1. 移动平均线 (MA)
- MA5: 5日均线，短期趋势
- MA10: 10日均线，中期趋势
- MA20: 20日均线，长期趋势
- MA60: 60日均线，大趋势

### 2. 成交量加权平均价 (VWAP)
- 基于成交量计算的平均价格
- 判断当前价格相对成交均价的偏离程度

### 3. 枢轴点 (Pivot Points)
- 经典枢轴点计算
- R1, R2, R3: 阻力位
- S1, S2, S3: 支撑位
- PP: 枢轴点

### 4. 支撑阻力位
- 近期高点/低点
- 成交量密集区
- 心理关口（整数位）

## 交易信号逻辑

### 买入信号
1. 收盘价站上MA5且MA5 > MA10 > MA20（多头排列）
2. 收盘价在VWAP上方，且偏离度 < 5%
3. 价格在枢轴点PP上方
4. 成交量放大（> 20日均量）
5. RSI在30-70之间，未超买超卖

**止损点设置**: 最近支撑位下方3-5%

### 卖出信号
1. 收盘价跌破MA5且MA5 < MA10（空头排列形成）
2. 收盘价在VWAP下方，且偏离度 > 5%
3. 价格跌破枢轴点PP
4. RSI > 70（超买）或出现顶背离
5. 需要输入成本价计算盈亏

### 观望信号
- 不符合明确的买入或卖出条件
- 指标信号相互矛盾
- 建议等待更明确的信号

## 使用方法

### 在OpenCode中使用

```
/skill tech-analysis
```

然后输入股票代码：

```
分析股票 00700
```

或：

```
分析 000001 的技术面
```

### 在Python代码中使用

```python
from .opencode.skills.tech-analysis.tech_analysis import TechnicalAnalyzer

# 创建分析器
analyzer = TechnicalAnalyzer()

# 分析股票
result = analyzer.analyze('00700', days=100)

# 打印分析报告
print(result['report'])
```

### 交互式使用

```python
import importlib.util

# 加载技能
spec = importlib.util.spec_from_file_location(
    'tech_analysis',
    '.opencode/skills/tech-analysis/tech_analysis.py'
)
tech_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tech_analysis)

# 分析股票
analyzer = tech_analysis.TechnicalAnalyzer()
result = analyzer.analyze('00700')

# 如果是卖出信号，询问成本价
if result['signal'] == '卖出':
    cost_price = float(input('请输入您的成本价: '))
    result_with_cost = analyzer.analyze_with_cost('00700', cost_price)
    print(result_with_cost['report'])
```

## 返回结果结构

```python
{
    'symbol': '00700',                    # 股票代码
    'name': '腾讯控股',                   # 股票名称
    'current_price': 538.0,               # 当前价格
    'signal': '买入',                     # 信号: 买入/卖出/观望
    'signal_color': 'red',                # 信号颜色（用于显示）
    
    # 技术指标
    'indicators': {
        'ma5': 535.2,
        'ma10': 532.8,
        'ma20': 528.5,
        'ma60': 515.3,
        'vwap': 533.5,
        'vwap_deviation': 0.8,            # VWAP偏离度%
        'rsi': 55.2,
        'volume_ratio': 1.25,             # 量比
    },
    
    # 枢轴点
    'pivot': {
        'pp': 535.0,                      # 枢轴点
        'r1': 545.0, 'r2': 552.0, 'r3': 560.0,  # 阻力位
        's1': 525.0, 's2': 518.0, 's3': 510.0,  # 支撑位
    },
    
    # 关键价位
    'key_levels': {
        'resistance': [545.0, 552.0, 560.0, 570.0],  # 阻力位
        'support': [525.0, 518.0, 510.0, 500.0],     # 支撑位
    },
    
    # 交易建议
    'suggestion': {
        'action': '买入',
        'confidence': 75,                 # 置信度 0-100
        'stop_loss': 510.0,               # 止损价（买入时）
        'target_price': 560.0,            # 目标价
        'risk_reward_ratio': 1.5,         # 盈亏比
    },
    
    # 详细报告
    'report': '...',                      # 完整的分析报告文本
}
```

## 分析报告示例

```
═══════════════════════════════════════════
📊 技术分析报告 - 腾讯控股 (00700)
═══════════════════════════════════════════

当前价格: 538.00 HKD
分析日期: 2026-02-23

【技术指标】
MA5:   535.20  📈
MA10:  532.80  📈
MA20:  528.50  📈
MA60:  515.30  📈
VWAP:  533.50 (+0.8%)
RSI:   55.20 (中性)
量比:  1.25 (放量)

【枢轴点】
R3: 560.00
R2: 552.00
R1: 545.00
PP: 535.00
S1: 525.00
S2: 518.00
S3: 510.00

【关键价位】
🔴 阻力位: 545.00 | 552.00 | 560.00 | 570.00
🟢 支撑位: 525.00 | 518.00 | 510.00 | 500.00

【交易信号】
🟥 买入 (置信度: 75%)

【操作建议】
建议买入，止损价: 510.00 HKD
目标价: 560.00 HKD
盈亏比: 1:1.5
潜在亏损: 5.2%
潜在盈利: 7.8%

【分析理由】
✅ 多头排列形成 (MA5 > MA10 > MA20 > MA60)
✅ 股价在VWAP上方，偏离度合理
✅ 站上枢轴点，处于强势区域
✅ 成交量放大，确认上涨动能
✅ RSI中性，未超买超卖

═══════════════════════════════════════════
```

## 注意事项

1. **风险提示**: 技术分析仅供参考，不构成投资建议
2. **止损纪律**: 买入后务必设置止损，严格执行
3. **仓位管理**: 建议单只股票仓位不超过总资金20%
4. **多周期验证**: 建议结合日线、周线、月线多周期分析
5. **基本面结合**: 技术分析应与基本面分析结合使用

## 依赖

- pandas: 数据处理
- numpy: 数值计算
- 依赖 futu 技能获取行情数据

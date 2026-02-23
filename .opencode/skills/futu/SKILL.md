---
name: futu
description: 通过Futu Open API获取股票行情数据，自动识别A股、港股、美股等不同市场的股票代码
---

## 功能概述

本技能用于从富途开放平台（Futu Open API）获取股票行情数据，支持：

- 自动识别股票代码所属市场（A股、港股、美股、A股ETF）
- 获取历史K线数据（日K、周K、月K）
- 支持前复权和后复权数据
- 获取实时快照数据

## 使用前提

1. 必须先启动 Futu OpenD 服务（运行在 127.0.0.1:11111）
2. Python 环境已安装 futu-api 库

## 使用方法

### 方式一：使用 `skill` 工具加载

在 OpenCode 中，可以使用 `skill` 工具加载此技能：

```
/skill futu
```

然后可以直接使用以下函数：

- `get_klines(symbol, period, start_date, end_date, adjust_flag)` - 获取K线数据
- `identify_market(symbol)` - 识别市场类型
- `format_futu_code(symbol)` - 格式化为Futu代码

### 方式二：在代码中导入

```python
import sys
import os
import importlib.util

# 动态加载技能模块
spec = importlib.util.spec_from_file_location(
    "futu_api", 
    ".opencode/skills/futu/futu_api.py"
)
futu_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(futu_api)

# 使用便捷函数获取K线数据
df = futu_api.get_klines(
    symbol='00700',              # 股票代码
    period='daily',              # 周期：daily/weekly/monthly
    start_date='2024-01-01',     # 开始日期
    end_date='2024-12-31',       # 结束日期
    adjust_flag='qfq'            # 复权：qfq(前复权)/hfq(后复权)
)
```

### 方式三：使用类方式

```python
from .opencode.skills.futu.futu_api import FutuAPI

# 初始化API（可自定义OpenD地址）
api = FutuAPI(host='127.0.0.1', port=11111)

# 获取K线数据
df = api.get_klines(
    symbol='00700',
    period='daily',
    start_date='2024-01-01',
    end_date='2024-12-31',
    adjust_flag='qfq'
)

# 获取实时快照
snapshot = api.get_snapshot('00700')
```

## 支持的市场和代码格式

| 市场 | 代码示例 | Futu格式 | 说明 |
|------|---------|---------|------|
| 港股 | 00700, 09988 | HK.00700, HK.09988 | 5位数字 |
| A股-深圳 | 000001, 002594 | SZ.000001, SZ.002594 | 6位数字，0/1/2/3开头 |
| A股-上海 | 600000, 688981 | SH.600000, SH.688981 | 6位数字，5/6/7/9开头 |
| A股ETF | 510500, 159915 | SH.510500, SZ.159915 | 6位数字，5/15开头 |
| 美股 | AAPL, TSLA | US.AAPL, US.TSLA | 字母代码 |

## 返回数据字段

获取的DataFrame包含以下字段：

- `股票代码`: Futu格式的代码（如 HK.00700）
- `股票名称`: 股票中文名称
- `日期`: 交易日期（YYYY-MM-DD格式）
- `开盘`: 开盘价
- `收盘`: 收盘价
- `最高`: 最高价
- `最低`: 最低价
- `成交量`: 成交量
- `成交额`: 成交金额
- `换手率`: 换手率
- `市盈率`: 市盈率
- `涨跌幅`: 涨跌幅(%)
- `昨收`: 昨日收盘价
- `涨跌额`: 涨跌额

## 完整示例

```python
import sys
import os
import importlib.util
from datetime import datetime, timedelta

# 加载技能
spec = importlib.util.spec_from_file_location(
    "futu_api", 
    ".opencode/skills/futu/futu_api.py"
)
futu_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(futu_api)

# 计算日期范围
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

# 获取腾讯控股(00700)的K线数据
df = futu_api.get_klines(
    symbol='00700',
    period='daily',
    start_date=start_date,
    end_date=end_date,
    adjust_flag='qfq'
)

# 取最近100个交易日
df_100 = df.tail(100)

print(f'获取到 {len(df_100)} 条数据')
print(df_100[['日期', '开盘', '收盘', '涨跌幅']].head())
```

## 错误处理

技能会在以下情况抛出 ValueError：

- 无法识别的股票代码类型
- OpenD服务未启动或连接失败
- 无效的开始/结束日期
- 不支持的数据周期或复权类型
- 获取数据失败或数据为空

## 注意事项

1. 必须先启动 Futu OpenD 服务才能获取数据
2. 首次获取某只股票数据可能需要较长时间
3. 默认每次请求最多1000条数据，超过会自动分页获取
4. 日期格式必须为 YYYY-MM-DD

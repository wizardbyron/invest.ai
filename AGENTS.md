# AGENTS.md - AI 代理指南

本文档为在 invest.ai 代码库中工作的 AI 代理提供指导。

在运行 Python 脚本前，需要通过 'source .venv/bin/activate' 激活虚拟环境。

## 构建、检查和测试命令

本项目使用 `uv` 进行依赖管理。

### 安装依赖
```bash
# 安装依赖
uv sync

# 更新锁文件
uv lock

# 添加新依赖
uv add <package-name>
```

### 运行测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest test/test_util.py

# 运行单个测试函数
uv run pytest test/test_util.py::test_numbers_in_chinese

# 以详细模式运行测试
uv run pytest -v
```

### 构建 Docker 镜像
```bash
./build.sh
```

### 代码质量
- 未配置显式的代码检查工具
- 提交前需要人工代码审查

## 代码风格指南

### 通用原则
- 编写清晰、可读且意图明确的代码
- 显式优于隐式
- 保持函数单一职责
- 为函数签名使用类型提示

### 导入
将导入分为三个部分，中间用空行分隔：
1. 标准库导入
2. 第三方库导入
3. 本地/相对导入

```python
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from src.data import history_klines
from src.util import remove_leading_spaces
```

### 命名约定
| 类型 | 约定 | 示例 |
|------|------------|---------|
| 函数 | snake_case | `remove_leading_spaces()` |
| 变量 | snake_case | `start_date`, `end_date` |
| 常量 | UPPER_SNAKE_CASE | `disclaimer_text` |
| 类型别名 | PascalCase | `DataFrame` |
| 私有辅助函数 | _prefix_snake_case | `_helper_function()` |

### 类型提示
为所有函数签名使用类型提示：
```python
def history_klines(
        symbol: str,
        period: str,
        start_date: str,
        end_date: str,
        adjust_flag: str = 'qfq') -> DataFrame:
```

### 文档字符串
为所有公共函数包含文档字符串：
```python
def identify_stock_type(code: str) -> str:
    """根据代码判断市场类型

    Args:
        code (str): 证券代码

    Returns:
        str: 市场类型
    """
```

### 错误处理
- 对无效参数使用 `ValueError`
- 对 I/O 操作使用 try/except
- 提供有意义的错误信息
```python
if symbol is None:
    raise ValueError("symbol is required")

try:
    df_symbols = pd.read_csv(df_symbol_cache)
except FileNotFoundError as e:
    df_symbols = ak.stock_us_spot_em()
```

### 环境变量
- 使用 `os.environ.get()` 进行配置
- 提供合理的默认值
```python
source = os.environ.get("DATA_SOURCE", "akshare")
```

### 字符串格式化
- 对简单插值使用 f-strings
- 对复杂情况使用 `.format()`
- 对多行字符串使用 `remove_leading_spaces()` 工具

### 数据处理
- 使用 pandas DataFrames 处理表格数据
- 使用描述性的中文列名（股票代码, 股票名称, 日期, 开盘, 收盘等）
- 在处理前验证 DataFrames 不为空
```python
if klines.empty:
    raise ValueError("没有数据，请检查参数")
```

### 日期/时间处理
- 使用带 `ZoneInfo` 的 `datetime` 处理时区时间
- 将日期以 'YYYY-MM-DD' 格式存储为字符串
- 对中国市场使用 `Asia/Shanghai` 作为默认时区

### 文件路径
- 使用相对于项目根目录的路径
- 将数据缓存在 `.cache/` 目录中
```python
df_symbol_cache = f".cache/us_symbols.csv"
```

### Git 工作流
- 为逻辑变更创建提交
- 编写清晰的提交信息
- 永远不要提交密钥或 `.env` 文件
- 提交前测试变更
- **永远不要自动提交或推送到远程仓库** - 始终先征求用户确认

### 在此代码库中工作
- 主要入口点：`agent.py`, `app.py`, `portfolio.py`, `guide.py`
- 核心逻辑在 `src/` 目录中
- 测试在 `test/` 目录中
- 数据源在 `input/portfolios/` 中
- 通过 `.env` 文件进行配置（从 `.env.example` 复制）

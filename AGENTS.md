# AGENTS.md - Guidelines for AI Agents

This document provides guidelines for AI agents working on the invest.ai codebase.

Before python scripts you need to activate virtual environment via 'source .venv/bin/activate'

## Build, Lint, and Test Commands

This project uses `uv` for dependency management. 

### Installing Dependencies
```bash
# Install dependencies
uv sync

# Update lockfile
uv lock

# Add a new dependency
uv add <package-name>
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest test/test_util.py

# Run a single test function
uv run pytest test/test_util.py::test_numbers_in_chinese

# Run tests with verbose output
uv run pytest -v
```

### Building Docker Image
```bash
./build.sh
```

### Code Quality
- No explicit linting tools are configured
- Manual code review is required before committing

## Code Style Guidelines

### General Principles
- Write clean, readable code with clear intent
- Prefer explicit over implicit
- Keep functions focused and single-purpose
- Use type hints for function signatures

### Imports
Organize imports in three sections with blank lines between:
1. Standard library imports
2. Third-party imports
3. Local/relative imports

```python
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from src.data import history_klines
from src.util import remove_leading_spaces
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `remove_leading_spaces()` |
| Variables | snake_case | `start_date`, `end_date` |
| Constants | UPPER_SNAKE_CASE | `disclaimer_text` |
| Type Aliases | PascalCase | `DataFrame` |
| Private Helpers | _prefix_snake_case | `_helper_function()` |

### Type Hints
Use type hints for all function signatures:
```python
def history_klines(
        symbol: str,
        period: str,
        start_date: str,
        end_date: str,
        adjust_flag: str = 'qfq') -> DataFrame:
```

### Docstrings
Include docstrings for all public functions:
```python
def identify_stock_type(code: str) -> str:
    """根据代码判断市场类型

    Args:
        code (str): 证券代码

    Returns:
        str: 市场类型
    """
```

### Error Handling
- Use `ValueError` for invalid arguments
- Use try/except for I/O operations
- Provide meaningful error messages
```python
if symbol is None:
    raise ValueError("symbol is required")

try:
    df_symbols = pd.read_csv(df_symbol_cache)
except FileNotFoundError as e:
    df_symbols = ak.stock_us_spot_em()
```

### Environment Variables
- Use `os.environ.get()` for configuration
- Provide sensible defaults
```python
source = os.environ.get("DATA_SOURCE", "akshare")
```

### String Formatting
- Use f-strings for simple interpolation
- Use `.format()` for complex cases
- Use `remove_leading_spaces()` utility for multi-line strings

### Data Handling
- Use pandas DataFrames for tabular data
- Use descriptive Chinese column names (股票代码, 股票名称, 日期, 开盘, 收盘, etc.)
- Validate DataFrames are not empty before processing
```python
if klines.empty:
    raise ValueError("没有数据，请检查参数")
```

### Date/Time Handling
- Use `datetime` with `ZoneInfo` for timezone-aware times
- Store dates as strings in 'YYYY-MM-DD' format
- Use `Asia/Shanghai` as default timezone for Chinese markets

### File Paths
- Use relative paths from project root
- Cache data in `.cache/` directory
```python
df_symbol_cache = f".cache/us_symbols.csv"
```

### Git Workflow
- Create commits for logical changes
- Write clear commit messages
- Never commit secrets or `.env` files
- Test changes before committing
- **NEVER automatically commit or push to remote repository** - always ask user for confirmation first

### Working with This Repository
- Main entry points: `agent.py`, `app.py`, `portfolio.py`, `guide.py`
- Core logic in `src/` directory
- Tests in `test/` directory
- Data sources in `input/portfolios/`
- Configuration via `.env` file (copy from `.env.example`)

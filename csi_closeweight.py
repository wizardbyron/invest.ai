import pandas as pd
import time

index_symbols = {
    '000300': '沪深300',
    '000905': '中证500',
    # '930050': '中证A50',
    '000510': '中证A500',
    # '000688': '科创50',
    '931643': '双创50',
    '932365': '中证现金流',
    # '000015': '上证红利',
}


df = pd.DataFrame()

for index in index_symbols.keys():
    url = f'https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/closeweight/{index}closeweight.xls'
    df_index = pd.read_excel(url)
    if df is None:
        df = df_index.copy()
    else:
        df = pd.concat([df, df_index], axis=0)
    print(f'【{index_symbols[index]}】已获取{len(df_index)}条数据, 共{len(df)}条数据')
    time.sleep(5)

df.to_csv("output/index_all.csv", index=False, encoding='utf-8-sig')


print(df.groupby('成份券名称Constituent Name')[
      '权重(%)weight'].sum().sort_values(ascending=False)[:10])

# print(df.sort_values(by=['权重(%)weight'], ascending=False).head(10))

# df = df.sort_values(by=['权重(%)weight'], inplace=True, ascending=False)

# print(df)

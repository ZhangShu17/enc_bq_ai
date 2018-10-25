# coding:utf-8

import pandas as pd
from pandas import DataFrame, Series

df_empty = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
print(df_empty)
a1 = DataFrame({'A': [10], 'B': [20], 'C': [30], 'D': [40]})
df_empty = df_empty.append(a1, ignore_index=True)
a2 = DataFrame({'A': ['ssss'], 'B': ['5633'], 'C': ['7883'], 'D': None})
a3 = DataFrame({'A': ['ssss'], 'B': ['5633'], 'C': ['7883'], 'D': None})
df_empty = df_empty.append(a2, ignore_index=True)
df_empty = df_empty.append(a3, ignore_index=True)
result = df_empty.loc[df_empty['A'] == 'ssss']
print(df_empty)
print(result)
result['A'] = 'BBBBBB'
result['D'] = 'jnjnjn'
print(result)
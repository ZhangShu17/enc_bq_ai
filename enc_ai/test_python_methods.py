# coding:utf-8

import pandas as pd
from pandas import DataFrame, Series

# df_empty = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
# print(df_empty)
# a1 = DataFrame({'A': [10], 'B': [20], 'C': [30], 'D': [40]})
# df_empty = df_empty.append(a1, ignore_index=True)
# a2 = DataFrame({'A': ['ssss'], 'B': ['5633'], 'C': ['7883'], 'D': None})
# a3 = DataFrame({'A': ['ssss'], 'B': ['5683'], 'C': ['7883'], 'D': [[1,2,3]]})
# df_empty = df_empty.append(a2, ignore_index=True)
# df_empty = df_empty.append(a3, ignore_index=True)
# result = df_empty.loc[df_empty['A'] == 'ssss']
# print(df_empty.index[0])


# a=[[1, 2, 3, 4], [7,8,9,10]]
# a1=filter(lambda x: x[2]==99, a)
# print(a1)
# if a1:
# 	print('exist')
# else:
# 	print('not exist')


# def get(b=None):
# 	return 1 if not b else b
#
# print(get(b=100))

d1 = {1:23, 'b': 62}
d2 = {1:24, 'b': 2}
d3 = {1:23, 'b': 54}
d4 = {1:23, 'b': 1}
d5 = {1:1, 'b': 9}
d6 = {1:23, 'b': 32}
d7 = {1:5, 'b': 33}
d8 = {1:39, 'b': 100}
li = [d1, d2, d3, d4, d5, d6, d7, d8]
li.sort(key=lambda e: e['b'])  # 现根据'b'进行排序，优先级较低
print(li)

li.sort(key=lambda e: e[1])  # 再根据1进行排序，优先级高于'b'
print(li)






















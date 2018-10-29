# coding:utf-8

import pandas as pd
import numpy as np
import os


def chang_int4_int6(grid_data, map_id_4):
	index = grid_data.loc[grid_data['pos4'] == map_id_4].index[0]
	return grid_data.ix[index]['pos6']


def chang_int6_int4(grid_data, map_id_6):
	index = grid_data.loc[grid_data['pos6'] == map_id_6].index[0]
	return grid_data.ix[index]['pos4']


def get_int4_int6():
	pwd = os.getcwd()
	csv_path = pwd+'/tools/res_pos_cvt.csv'
	return pd.read_csv(csv_path)


def get_view_data():
	pwd = os.getcwd()
	csv_path = pwd + '/tools/res_pos_view.csv'
	data = pd.read_csv(csv_path)
	for index, row in data.iterrows():
		if str(row['view4_Set']) == 'nan':
			data.drop(axis=0, index=index, inplace=True)
	return data


motor_driven = [1627, 1628, 1724, 1726, 1727, 1728, 1825, 1826, 1827,
					   1828, 1923, 1924, 1925, 1927, 1928, 1929, 2024,
					   2025, 2026, 2027, 2028, 2029, 2125, 2126, 2127,
					   2226, 2227, 2228]

moter_driven_path = [[1926, 1827, 1727, 1627],
					 [1926, 1827, 1727, 1628],
					 [1926, 1925, 1825, 1724],
					 [1926, 1827, 1726],
					 [1926, 1827, 1727],
					 [1926, 1927, 1828, 1728],
					 [1926, 1925, 1825],
					 [1926, 1826],
					 [1926, 1827],
					 [1926, 1927, 1828],
					 [1926, 1925, 1924, 1923],
					 [1926, 1925, 1924],
					 [1926, 1925],
					 [1926, 1927],
					 [1926, 1927, 1928],
					 [1926, 1927, 1928, 1929],
					 [1926, 2026, 2025, 2024],
					 [1926, 2026, 2025],
					 [1926, 2026],
					 [1926, 2027],
					 [1926, 2027, 2028],
					 [1926, 2027, 2028, 2029],
					 [1926, 2026, 2125],
					 [1926, 2027, 2126],
					 [1926, 2027, 2127],
					 [1926, 2026, 2125, 2226],
					 [1926, 2027, 2127, 2227],
					 [1926, 2027, 2127, 2228]
					 ]

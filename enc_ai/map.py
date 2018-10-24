# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

map_data_frame = pd.read_csv('map2.csv')
print(map_data_frame.loc[map_data_frame['MapID'] == np.int64(80048)])
print(type(map_data_frame['MapID'][0]))

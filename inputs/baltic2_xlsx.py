# A parser for baltic-2 wind farm data.

import os
import pathlib
import pandas as pd
import numpy as np


class baltic2_xlsx:
    """Baltic-2 wind farm data class
    """

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), str(info['path'])
            )
        self.var = info['var']
        self.target_var = info['target_var']

    def get_ts(self, lev):

        file = os.path.join(self.path, 'Baltic2_wfdata.xlsx')

        df = pd.read_excel(file, sheet_name='data')

        df['t'] = df['t'].str.rsplit('+').str.get(0)
        df = df.set_index('t').sort_index()
        df.index = pd.to_datetime(df.index)

        # Convert local time to UTC time
        df.index = df.index-pd.Timedelta('1h')

        df = df.iloc[:, :3]

        if self.var == 'ws':
            var_col = 'Wind speed (m/s)'
        if self.var == 'power':
            var_col = 'Measurements (MW)'

        df = df[[var_col]]
        df.rename(columns={var_col: self.target_var}, inplace=True)

        return df

# A parser for multiple FINO2 .dat files in a directory.

import os
import pathlib
import pandas as pd
import numpy as np
import glob
import sys


class fino2_dats:
    """FINO2 data class
    """

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), str(info['path'])
            )
        self.var = info['var']
        # self.lev = conf['levels']['height_agl']
        self.target_var = info['target_var']

    def get_ts(self, lev):
        """The directory can contain multiple FINO2 files, and each file
        contains data at one height level.
        The function only read in one data file at one height level.
        """

        file_list = glob.glob(os.path.join(self.path, '*.dat'))

        for file in file_list:

            if str(lev)+'m' in file:

                df_all = pd.read_csv(file)

                # Get variable name and column names
                var_name = df_all.iloc[0][0].split(': ', 1)[1]
                col_names = df_all.iloc[3][0].split('\t')[1:]

                df = pd.read_csv(file, skiprows=6, sep='\s+')

                # Turn column names into 1st row
                df = pd.DataFrame(np.vstack([df.columns, df]))

                # Combine 2 time columns, hard coded
                df['t'] = df[0].map(str)+' '+df[1]

                # Drop duplicating columns
                df.pop(0)
                df.pop(1)

                # Reassign column names
                for i in range(len(col_names)):
                    df[col_names[i]] = df[i+2]
                    df.pop(i+2)

                df = df.set_index('t').sort_index()
                df.index = pd.to_datetime(df.index)

                # FINO data are averages centered at each 10-minute period
                # Data between 10:30 and 10:40 are averaged and labelled as
                # 10:35
                # Apply correction to label data at the end of each period
                # Hence data between 10:30 and 10:40 are averaged and labelled
                # as 10:40
                df.index = df.index+pd.Timedelta('5minutes')

                # Extract only 1 column of data
                out_df = df.loc[:, [self.var]]
                out_df.rename(
                    columns={self.var: self.target_var}, inplace=True
                    )
                out_df = out_df.astype(float)

                return out_df

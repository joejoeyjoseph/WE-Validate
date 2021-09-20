# This class processes power curve from a csv file.

import os
import pathlib
import importlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tools import eval_tools


class pc_csv:
    """Power curve class, using power curve from a csv file."""

    def __init__(self, path, file, ws, power, hhws_df, hub_height, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), str(path)
            )
        self.file = os.path.join(self.path, file)

        self.ws = ws
        self.power = power
        # Declare hub height wind speed data frame
        self.hhws_df = hhws_df
        self.hh = hub_height
        self.conf = conf

        self.conf['reference']['var'] = self.power
        self.plotting = eval_tools.get_module_class('plotting', 'plot_data')(
            self.conf)

    def get_power(self):
        """Convert wind speed into power using user-provided power curve."""

        self.pc_df = pd.read_csv(self.file)

        # Assume 0 power in the beginning
        power_df = pd.DataFrame(
            0, columns=self.hhws_df.columns+'_derived_power',
            index=self.hhws_df.index
            )

        # For each dataset (i.e. each column in data frame)
        for hh_col, p_col in zip(self.hhws_df.columns, power_df.columns):

            # When wind speed is nan, assign power to nan
            power_df.loc[np.isnan(self.hhws_df[hh_col]), p_col]\
                    = np.NaN

            # For each wind speed (bin) in power curve
            for i, row in self.pc_df.iterrows():

                # Assign respective power when wind speed exceeds threshold
                power_df.loc[self.hhws_df[hh_col] > row[self.ws], p_col]\
                    = row[self.power]

        self.power_df = power_df.sort_index()

        return self.power_df

    def plot_pc(self):
        """Plot power curve."""

        plt.plot(self.pc_df[self.ws], self.pc_df[self.power], c='k')

        for hh_col, p_col in zip(self.hhws_df.columns, self.power_df.columns):

            plt.scatter(self.hhws_df[hh_col], self.power_df[p_col])

        plt.show()

    def plot_power_ts(self):
        """Plot power time series."""

        self.plotting.plot_ts_line(self.power_df, self.hh, self_units=False)

    def plot_power_scatter(self):
        """Plot power scatterplot."""

        self.plotting.plot_pair_scatter(self.power_df, self.hh,
                                        self_units=False)

# This script contains ramp plotting functions.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class plot_ramp:
    """Class for plotting ramp results at 1 height level."""

    def __init__(self, ramp_df, combine_df, conf, lev, ramps):

        # Requires deep copy because this code changes self.df
        self.df = ramp_df.copy(deep=True)
        self.combine_df = combine_df
        self.duration = ramps['duration']
        self.var = conf['reference']['var']
        self.lev_units = conf['levels']['height_units']
        self.lev = lev

        if conf['reference']['units'] == 'ms-1':
            self.units = r'm $s^{-1}$'
        else:
            self.units = conf['reference']['units']

    def get_period_df(self, col):
        """Bundle groups of data based on continuous True/False signals.
        Find the first and last times of each group.
        """

        self.df['col_group'] = (
            self.df[col].diff(1) != 0).astype('int').cumsum()

        col_true = self.df.loc[self.df[col] == True]

        out_df = pd.DataFrame(
            {'start': col_true.groupby('col_group')['time'].first(),
             'end': col_true.groupby('col_group')['time'].last()}
            )

        return out_df

    def plot_ts_contingency(self):
        """Plot results of baseline and comparison ramp events.
        Plot periods of correct and incorrect ramp classification
        according to the 2x2 contingency table.
        Use midpoint of duration for plotting ramps.
        """

        self.df.index = self.df.index + (pd.to_timedelta(
            str(self.duration))/2)

        self.df['time'] = self.df.index

        tp_df = self.get_period_df('true_positive')
        fp_df = self.get_period_df('false_positive')
        fn_df = self.get_period_df('false_negative')
        tn_df = self.get_period_df('true_negative')

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        self.df.loc[self.df['base_ramp'] == 0, 'base_ramp'] = np.NaN
        self.df.loc[self.df['comp_ramp'] == 0, 'comp_ramp'] = np.NaN
        # To separate dots of baseline and comparison ramps on the plot
        self.df['comp_ramp'] = self.df['comp_ramp'] - 0.1

        # Plot time series
        for col in self.combine_df.columns:
            ax1.plot(self.combine_df.index, self.combine_df[col], label=col)

        ax1.set_title('comparison at '+str(self.lev)+' '+self.lev_units)
        ax1.set_ylabel(self.var+' ('+self.units+')')
        ax1.legend()

        # Plot ramp classification dots and 2x2 accuracy periods
        ax2.tick_params(left=False, labelleft=False)

        ax2.scatter(self.df.index, self.df['base_ramp'],
                    label='baseline ramp')
        ax2.scatter(self.df.index, self.df['comp_ramp'],
                    label='comparison ramp')

        def plot_df_period(df, y_min, y_max, color):
            for i, row in df.iterrows():
                ax2.axvspan(row['start'], row['end'], y_min, y_max,
                            color=color, alpha=0.7)

        plot_df_period(tp_df, 0.8, 1, 'dodgerblue')
        plot_df_period(tn_df, 0.8, 1, 'navy')

        plot_df_period(fp_df, 0, 0.2, 'red')
        plot_df_period(fn_df, 0, 0.2, 'purple')

        ax2.set_ylim([0.7, 1.2])
        ax2.set_ylabel('periods of classified ramps\n& ramp forecast results')
        ax2.tick_params(axis='x', labelrotation=90)
        ax2.set_xlabel('time')
        ax2.legend()

        ax2_fs = 12

        ax2.text(0.1, 0.71, 'true positive/hits', color='dodgerblue',
                 transform=ax2.transAxes, fontsize=ax2_fs)
        ax2.text(0.5, 0.71, 'true negative', color='navy',
                 transform=ax2.transAxes, fontsize=ax2_fs)

        ax2.text(0.1, 0.25, 'false positive/false alarm', color='red',
                 transform=ax2.transAxes, fontsize=ax2_fs)
        ax2.text(0.5, 0.25, 'false negative/misses', color='purple',
                 transform=ax2.transAxes, fontsize=ax2_fs)

        plt.show()

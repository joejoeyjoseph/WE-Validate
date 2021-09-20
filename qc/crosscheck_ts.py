# Perform crosscheck between two datasets

import pandas as pd
import sys


class crosscheck_ts:
    """Crosscheck time series of two datasets."""

    def __init__(self, conf):

        self.upper = conf['time']['window']['end']
        self.lower = conf['time']['window']['start']

        try:
            self.select_data = conf['reference']['select_data']
            self.select_method = conf['reference']['select_method']
        except KeyError:
            self.select_data = 'end'
            self.select_method = 'instance'

    def trim_ts(self, ts):
        """Trim time series to within upper and lower limits,
        as declared by users.
        """

        ts = ts.loc[ts.index >= self.lower]
        ts = ts.loc[ts.index <= self.upper]

        return ts

    def run_select_method(self, input):
        """Select data from the resampler according to the declared method.

        :param str average: arithmetic mean
        :param str instance: sample instance at the resampled time step
        """

        if self.select_method == 'average':
            output = input.mean()
        if self.select_method == 'instance':
            output = input.asfreq()

        return output

    def resample_to_freq(self, ts, freq):
        """Check the consistency of the time step frequency in a time series.
        Resample time series only if the user-defined data frequency is lower
        than the existing data frequency, and then derive new time series based
        on :func:`~crosscheck_ts.crosscheck_ts.run_select_method`.
        """

        time_diff = ts.index.to_series().diff()

        if len(time_diff[1:].unique()) == 1:

            if (freq > time_diff[1].components.minutes)\
               and (self.select_data == 'end'):

                ts = ts.resample(str(freq)+'T', label='right', closed='right')

                ts = self.run_select_method(ts)

                print()
                print('resampling '+ts.columns.values[0]+' every '+str(freq)
                      + ' minutes using the '+self.select_method+' method')

        else:

            print()
            print(time_diff[1:].unique())
            sys.exit('ERROR: TIME SERIES DOES NOT HAVE CONSTANT TIME STEPS')

        return ts

    def align_time(self, base, c):
        """Align datetime indices of baseline and comparison datasets.
        When the length of the resultant combine data frame does not match
        the user-defined, desired data length, print error messages.
        """

        base_data = self.trim_ts(base['data'])
        comp_data = self.trim_ts(c['data'])

        base_data = self.resample_to_freq(base_data, base['freq'])
        comp_data = self.resample_to_freq(comp_data, c['freq'])

        # Match time series data frequencies
        # Set baseline data time series as 1st column

        # If averaging method is not defined, then perform a simple merge
        # according to time indices
        if self.select_data is None:

            combine_df = pd.merge(
                base_data, comp_data, left_index=True, right_index=True)

            print()
            print('performing a simple merge between baseline and')
            print('comparison datasets according to time indices')

        # When declared data frequencies differ, resample according to
        # the time indicies of the lower-frequency dataset,
        # calculate the mean of data and record at the end of the time step
        elif self.select_data == 'end':

            if base['freq'] < c['freq']:

                base_data = base_data.resample(
                    str(c['freq'])+'T', label='right', closed='right',
                    origin=comp_data.index.min())

                base_data = self.run_select_method(base_data)

                print()
                print('aligning the '+str(base['freq'])+'-miniute baseline '
                      + 'data ('+base_data.columns.values[0]+') to match the ')
                print(str(c['freq'])+'-minute comparison data ('
                      + comp_data.columns.values[0]+'), at the end of the')
                print('measurement period using the '
                      + self.select_method+' method')

            if base['freq'] > c['freq']:

                comp_data = comp_data.resample(
                    str(base['freq'])+'T', label='right',
                    closed='right', origin=base_data.index.min())

                comp_data = self.run_select_method(comp_data)

                print()
                print('aligning the '+str(c['freq'])+'-miniute comparison '
                      + 'data ('+comp_data.columns.values[0]+') to match the ')
                print(str(base['freq'])+'-minute baseline data ('
                      + base_data.columns.values[0]+'), at the end of the')
                print('measurement period using the '
                      + self.select_method+' method')

            combine_df = pd.merge(
                base_data, comp_data, left_index=True, right_index=True)

        t_min = combine_df.index.min()
        t_max = combine_df.index.max()

        freq = (combine_df.index[1] - t_min).total_seconds() / 60.0
        diff_minute = (t_max - t_min).total_seconds() / 60.0

        print()
        print('evaluate '+', '.join(combine_df.columns.values)
              + ' from '+str(t_min)+' to '+str(t_max)
              )
        print('every '+str(freq)+' minutes, total of '+str(len(combine_df))
              + ' time steps')

        # data_len = (diff_minute + freq) / freq

        desired_period_minute = (self.upper - self.lower).total_seconds()\
            / 60.0

        desired_len = (desired_period_minute + freq) / freq

        if diff_minute != desired_period_minute:

            print()
            print('!!!!!!!!!!')
            print('WARNING: DESIERED EVALUATION DURATION DOES NOT MATCH '
                  + 'DATA DURATION'
                  )
            print('DESIRED: FROM '+str(self.lower)+' TO '+str(self.upper))
            print('DATA: FROM '+str(t_min)+' TO '+str(t_max))
            print('!!!!!!!!!!')

        # Correct
        if len(combine_df) == desired_len:

            pass

        else:

            print()
            print('!!!!!!!!!!')
            print('WARNING: DATA FREQUENCY DOES NOT MATCH DESIRED '
                  + 'EVALUATION PERIOD FREQUENCY')
            print('SHOULD HAVE '+str(desired_len)+' TIME STEPS IN DATA')
            print('ONLY HAVE '+str(len(combine_df))+' TIME STEPS IN DATA')
            print('!!!!!!!!!!')

        return combine_df

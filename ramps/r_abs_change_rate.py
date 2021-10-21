# Ramp change rate
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class r_abs_change_rate:

    def __init__(self, conf, c, ramp_data, ramps):

        self.base_var = conf['base']['target_var']
        self.comp_var = c['target_var']
        self.ramps = ramps
        self.ramp_data = ramp_data
        self.reference = conf['reference']
        self.ramp_nature = 'all'

    def get_rampdf(self):
        """Generate data frame with ramp classification."""

        print()
        print('classfy as a ramp event when |'+self.reference['var']
              + '| exceeds '+str(self.ramps['percent'])+'% of '
              + self.ramps['rated']+self.reference['units']+' in a window of '
              + self.ramps['duration']
              )

        ramp_data_dn = self.ramp_data.copy()
        ramp_data_dn.index = ramp_data_dn.index - pd.to_timedelta(
            str(self.ramps['duration']))

        # Get data frame of lagged differences
        # Drop NA means dropping data points on both starting and ending
        # points of a ramp period
        ramp_df = (ramp_data_dn - self.ramp_data).dropna()

        zeros_col = np.zeros(len(ramp_df))
        ramp_df['base_ramp'] = zeros_col
        ramp_df['comp_ramp'] = zeros_col

        thres = self.ramps['rated']*self.ramps['percent']/100.

        ramp_df.loc[abs(ramp_df[self.base_var])
                    > thres, ['base_ramp']] = 1
        ramp_df.loc[abs(ramp_df[self.comp_var])
                    > thres, ['comp_ramp']] = 1

        return ramp_df

    def get_ramp_method_name(self):
        """Get ramp method name as column name in output file."""

        return self.ramps['definition']+'_'+str(self.ramps['percent'])+'%_'\
            + self.ramps['rated']+self.reference['units']+'_'+self.ramps['duration']
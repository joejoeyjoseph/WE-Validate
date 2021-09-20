# Classify up ramp or down ramp event based on the difference
# between two points (ramp magnitude) at the start and end of a
# predefined duration.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class r_magnitude:

    def __init__(self, conf, c, ramp_data, ramps):

        self.base_var = conf['base']['target_var']
        self.comp_var = c['target_var']
        self.ramps = ramps
        self.ramp_data = ramp_data
        self.reference = conf['reference']

        if self.ramps['magnitude'] > 0:
            self.ramp_nature = 'up'
        elif self.ramps['magnitude'] < 0:
            self.ramp_nature = 'down'

    def get_rampdf(self):
        """Generate data frame with ramp classification."""

        print()
        print('classfy as '+self.ramp_nature+' ramp event when '
              + 'the change of '+self.reference['var']
              + ' exceeds '+str(self.ramps['magnitude'])
              + ' '+self.reference['units']+' in '
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

        if self.ramps['magnitude'] > 0:

            ramp_df.loc[ramp_df[self.base_var]
                        > self.ramps['magnitude'], ['base_ramp']] = 1
            ramp_df.loc[ramp_df[self.comp_var]
                        > self.ramps['magnitude'], ['comp_ramp']] = 1

        elif self.ramps['magnitude'] < 0:

            ramp_df.loc[ramp_df[self.base_var]
                        < self.ramps['magnitude'], ['base_ramp']] = 1
            ramp_df.loc[ramp_df[self.comp_var]
                        < self.ramps['magnitude'], ['comp_ramp']] = 1

        return ramp_df

    def get_ramp_method_name(self):
        """Get ramp method name as column name in output file."""

        return self.ramps['definition']+'_'+str(self.ramps['magnitude'])\
            + self.reference['units']+'_'+self.ramps['duration']

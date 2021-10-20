# Ramp change rate
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class r_abs_change_rate:

    def __init__(self, conf, c, ramp_data, ramps):

        self.base_var = conf['base']['target_var']
        self.comp_var = c['target_var']
        self.ramps = ramps
        self.ramp_data = ramp_data
        self.reference = conf['reference']
        self.ramp_nature = 'all'

    def compute(self, x, y):

        # x is baseline
        return float(np.mean(y - x))

    def get_ramp_method_name(self):
        """Get ramp method name as column name in output file."""

        return self.ramps['definition']+'_'+str(self.ramps['percent'])\
            + self.reference['units']+'_'+self.ramps['duration']
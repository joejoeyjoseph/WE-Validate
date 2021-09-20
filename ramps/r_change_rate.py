# Ramp change rate
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class r_change_rate:

    

    def compute(self, x, y):

        # x is baseline
        return float(np.mean(y - x))

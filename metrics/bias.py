# This is a simple average bias calculation,
# bias = mean(y - x),
# assuming x is the truth.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class bias:

    def compute(self, x, y):

        # x is baseline
        return float(np.mean(y - x))

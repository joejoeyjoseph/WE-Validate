# This is a simple average mae calculation, mae = mean(|x - y|).
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class mae:

    def compute(self, x, y):

        return float(np.mean(abs(x - y)))

# This is a simple median absolute error calculation, mdae = median(|x - y|).
# This metric is statistically robust and resistant with a linear penalty. 
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class mdae:

    def compute(self, x, y):

        return float(np.median(abs(x - y)))

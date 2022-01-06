# This performs a normalized root mean squared error (nRMSE)
# calculation, essentially calculate rmse using normalized data:
# nrmse = root(mean( ( (x/mean(x)) - (y/mean(y)) )^2 ))
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class nrmse:

    def compute(self, x, y):

        x_norm = x/np.mean(x)
        y_norm = y/np.mean(y)

        return float(np.sqrt(np.mean((x_norm - y_norm)**2)))

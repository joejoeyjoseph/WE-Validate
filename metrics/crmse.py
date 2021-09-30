# This performs a centered (or unbiased) root mean squared error (cRMSE)
# calculation, essentially calculate rmse using de-meaned data:
# crmse = root(mean( ( (x - mean(x)) - (y - mean(y)) )^2 ))
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class crmse:

    def compute(self, x, y):

        x_demean = x - np.mean(x)
        y_demean = y - np.mean(y)

        return float(np.sqrt(np.mean((x_demean - y_demean)**2)))

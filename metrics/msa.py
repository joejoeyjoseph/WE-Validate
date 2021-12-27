# This median symmetric accuracy
# assuming x is the truth
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class msa:

    def compute(self, x, y):

        q = y/x
        median = np.nanmedian(np.abs(np.log(q)))

        return (np.exp(median) - 1)*100

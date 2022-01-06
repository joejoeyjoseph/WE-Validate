# This is a simple average percent absolute error calculation,
# mae % = mean(100 * |x - y| / x),
# assuming x is the truth.
#
# Mask invalid values to calculate percentage, in case x is 0.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class mdae_pct:

    def compute(self, x, y):

        fraction_array = np.ma.masked_invalid(abs(x - y) / x)

        invalid_num = fraction_array.mask.sum()

        if invalid_num > 0:

            print()
            print('- in calculating mae percentage, '
                  + str(invalid_num)+' invalid data points, which would have')
            print('led to undefined results '
                  + '(e.g., division by zero), are ignored.')

        return float(np.median(100 * fraction_array))

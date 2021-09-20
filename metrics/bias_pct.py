# This is a simple average percent bias calculation,
# bias % = mean(100 * (y - x) / x),
# assuming x is the truth.
#
# Mask invalid values to calculate percentage, in case x is 0.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np


class bias_pct:

    def compute(self, x, y):

        # x is baseline
        fraction_array = np.ma.masked_invalid((y - x) / x)

        invalid_num = fraction_array.mask.sum()

        if invalid_num > 0:

            print()
            print('- in calculating bias percentage, '
                  + str(invalid_num)+' invalid data points, which would have')
            print('led to undefined results '
                  + '(e.g., division by zero), are ignored.')

        return float(np.mean(100 * fraction_array))

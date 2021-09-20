# This script calculates and prints metrics results.

import numpy as np
import itertools
from tools import eval_tools
import sys


def remove_na(combine_df, ramp_txt=False):

    compute_df = combine_df.dropna()

    only_na = combine_df[~combine_df.index.isin(compute_df.index)]

    if ramp_txt is True:
        print_txt = 'ramp skill scores'
    else:
        print_txt = 'metrics'

    print()
    print('to calculate '+print_txt+', removing the following time steps ')
    print('that contain NaN values:')
    print(only_na.index.strftime('%Y-%m-%d %H:%M:%S').values)
    print()
    print('hence, only use '+str(len(compute_df))
          + ' time steps in data to calculate '+print_txt)

    return compute_df


def run(combine_df, metrics, results, ind, c, conf, base, lev):
    """Calculate metrics and print results.
    Remove NaNs in data frame.
    For each data column combination, split into baseline and
    compare data series.
    Calculate and print metrics, as listed in the yaml file.
    """

    compute_df = remove_na(combine_df)

    # For future purposes,
    # In case of reading in mulitple compare data columns
    for pair in itertools.combinations(compute_df.columns, 2):

        # Baseline should be the 1st (Python's 0th) column
        x = compute_df[pair[0]]
        y = compute_df[pair[1]]

        if len(x) != len(y):

            sys.exit('Lengths of baseline and compare datasets are'
                     + ' not equal!'
                     )

        if base['nature'] == 'wd' and c['nature'] == 'wd':

            print()
            print('calculating differences in wind directions after converting'
                  + ' them into unit vectors')

            y = eval_tools.get_wd_angle_diff_series(x, y)
            # x as baseline, is set to zero
            x = np.zeros(len(y))

        for m in metrics:

            results[ind][m.__class__.__name__] = m.compute(x, y)

        print()
        print('==-- '+conf['reference']['var']+' metrics: '+c['name']
              + ' - '+base['name']+' at '+str(lev)+' '
              + conf['levels']['height_units']+' --=='
              )
        print()

        for key, val in results[ind].items():

            if isinstance(val, float):

                end_units = ''
                suffix_pct = 'pct'

                if str(key).endswith(suffix_pct):
                    end_units = '%'

                print(str(key)+': '+str(np.round(val, 3))+end_units)

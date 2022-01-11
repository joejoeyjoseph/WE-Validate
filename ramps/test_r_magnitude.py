# This script runs unit tests for r_magnitude.
# Test for up ramps.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import pandas as pd
import numpy as np
import math
from pandas._testing import assert_frame_equal

from tools import eval_tools

test_dir = 'ramps'

conf_up_eg = {'base': {'target_var': 'base_col'},
           'ramps': {'duration': '2 hours', 'magnitude': 2},
           'reference': {'var': 'wind speed', 'units': 'ms-1'}
           }

ramps_up_eg = conf_up_eg['ramps']

c_eg = {'target_var': 'comp_col'}

index_eg = pd.to_datetime(pd.Series(
    ['2020-10-31 00:00', '2020-10-31 01:00',
     '2020-10-31 02:00', '2020-10-31 03:00',
     '2020-10-31 04:00', '2020-10-31 05:00',
     '2020-10-31 06:00', '2020-10-31 07:00',
     '2020-10-31 08:00', '2020-10-31 09:00',
     '2020-10-31 10:00', '2020-10-31 11:00', 
     '2020-10-31 12:00', '2020-10-31 13:00']))

data_eg = {
    'base_col': [60, 59, 40, 41, 42, 43, 20, 21, 40, 42, 40, 42, 50, 52],
    'comp_col': [20, 21, 22, 23, 40, 41, 40, 41, 60, 62, 60, 62, 60, 62],
}
ramp_data_eg = pd.DataFrame(data_eg, index=index_eg)

ramp_df_eg = ramp_data_eg.copy()
ramp_df_eg = ramp_df_eg.iloc[:-2]
ramp_df_eg['base_col'] = np.array(
    [-20, -18, 2, 2, -22, -22, 20, 21, 0, 0, 10, 10], float
    )
ramp_df_eg['comp_col'] = np.array([2, 2, 18, 18, 0, 0, 20, 21, 0, 0, 0, 0], float)
ramp_df_eg['base_ramp'] = np.array([0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1], float)
ramp_df_eg['comp_ramp'] = np.array([0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0], float)

ramp_ss_eg = ramp_df_eg.copy()
ramp_ss_eg['true_positive'] = np.array(
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], dtype=bool
    )
ramp_ss_eg['false_positive'] = np.array(
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=bool
    )
ramp_ss_eg['false_negative'] = np.array(
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=bool
    )
ramp_ss_eg['true_negative'] = np.array(
    [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0], dtype=bool
    )


def read_ramp(ramp_method):

    return eval_tools.get_module_class(test_dir, ramp_method)


def test_r_magnitude():

    r = read_ramp('r_magnitude')(conf_up_eg, c_eg, ramp_data_eg, ramps_up_eg)

    assert_frame_equal(r.get_rampdf(), ramp_df_eg)


def test_add_contingency_table():

    df = read_ramp('process_ramp')(ramp_df_eg).add_contingency_table()

    assert_frame_equal(df, ramp_ss_eg)


def get_contingency_table():

    ramp_obj = read_ramp('process_ramp')(ramp_df_eg)
    _ = ramp_obj.add_contingency_table()

    return ramp_obj


def test_true_pos():

    assert get_contingency_table().true_pos == 2


def test_false_pos():

    assert get_contingency_table().false_pos == 2


def test_false_neg():

    assert get_contingency_table().false_neg == 2


def test_true_neg():
    assert get_contingency_table().true_neg == 6


def test_cal_pod():

    assert math.isclose(
        get_contingency_table().cal_pod(), 0.5, rel_tol=1e-4
        )


def test_cal_csi():

    assert math.isclose(
        get_contingency_table().cal_csi(), 0.3333, rel_tol=1e-4
        )


def test_cal_fbias():

    assert math.isclose(
        get_contingency_table().cal_fbias(), 1, rel_tol=1e-4
        )


def test_cal_farate():

    assert get_contingency_table().cal_farate() == 0.25


def test_cal_fa():

    assert get_contingency_table().cal_fa() == 0.5

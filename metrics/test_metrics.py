# This script runs unit tests for metrics files.

import importlib
import pandas as pd
import math

from tools import eval_tools

test_dir = 'metrics'

# Example data series
x_eg = pd.Series([2, 2, 2, 2, 16])
y_eg = pd.Series([4, 5, 6, -7, 8])


def read_metric(metric):

    return eval_tools.get_module_class(test_dir, metric)()


def test_bias():

    assert read_metric('bias').compute(5, 4) == -1


def test_series_bias():

    assert read_metric('bias').compute(x_eg, y_eg) == -1.6


def test_bias_pct():

    assert read_metric('bias_pct').compute(5, 4) == -20


def test_series_bias_pct():

    assert read_metric('bias_pct').compute(x_eg, y_eg) == -10


def test_mae():

    assert read_metric('mae').compute(5, 4) == 1


def test_series_mae():

    assert read_metric('mae').compute(x_eg, y_eg) == 5.2


def test_mae_pct():

    assert read_metric('mae_pct').compute(5, 4) == 20


def test_series_mae_pct():

    assert read_metric('mae_pct').compute(x_eg, y_eg) == 190


def test_series_rmse():

    result = read_metric('rmse').compute(x_eg, y_eg)

    assert math.isclose(result, 5.899, rel_tol=1e-4)


def test_series_crmse():

    result = read_metric('crmse').compute(x_eg, y_eg)

    assert math.isclose(result, 5.678, rel_tol=1e-4)

# Metrics

This directory contains algorithms to compute timeseries comparison metrics.

A metric file reads in time series `x` and `y` and compute, where `x` is the baseline (truth or observed) dataset and `y` is the comparison (model) dataset. A metric file must contain the `compute` function for metric computation.

To add your own, simply copy an existing file or use the following template:

```
# The most fieriest metric in Westeros.
#
# Daenerys Targaryen <daenerys.targaryen@motherofdragons.got>

class dracarys:

    def compute(self, x, y):

        dragonfire = y - x

        return dragonfire

```

Please also add unit tests to `test_metrics.py`, as follows:

```
def test_dracarys():

    assert read_metric('dracarys').compute(0, 0) == 0

def test_series_dracarys():

    assert read_metric('dracarys').compute([0, 20], [10, 51]) == [10, 31]
```
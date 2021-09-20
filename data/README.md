# Data files

This directory contains input data -- one directory per input data.

The `mw_` directories contain the mountain wave demo case, and the `test_` directories contain the test datasets used by `config_test.yaml`. 

The power curve data are available at the [NREL Wind Turbine Power Curve Archive](https://github.com/NREL/turbine-models/). The demo case uses the 2018 U.S. market average power curve.

To add your own, simply create a directory for your data and list it in `config.yaml`.
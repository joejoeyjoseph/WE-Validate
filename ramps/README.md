# Ramps

This directory contains code relating to ramp classification. 

The scripts started with `r_` are ramp methods, e.g. `r_{ramp_definition}.py`. Each script contains one method that classifies ramp events according to a specific algorithm or definition. Each ramp method must
  * generate a output dataframe via a `get_rampdf` function.
  * classify ramp events in the baseline dataset as `base_ramp` and ramp events in the comparison dataset as `comp_ramp`.

To add your own, simply copy an existing file or use the following template (`r_sōvētēs.py`):

```
# The loftiest ramp defintion in Westeros.
#
# Daenerys Targaryen <daenerys.targaryen@motherofdragons.got>

class r_sōvētēs:

    def get_rampdf(self):

        ramp_df = fly

        return ramp_df

```

The `process_ramp.py` script is a collection of useful functions that are called in `ivalidate.py`, including: compares baseline and comparison ramp events and categorize the results based on a 2x2 contingency table, calculate ramp skill scores, etc.

For each ramp definition (`r_sōvētēs.py`), please also add unit tests as `test_r_sōvētēs.py`. 
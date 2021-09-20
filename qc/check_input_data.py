# Functions that check for irregularies in input data.

import os
import numpy as np
import pandas as pd

# For debugging
# pd.set_option('display.max_rows', None, 'display.max_columns', None)


def convert_mask_to_nan(var, t, mask_i):
    """Convert masked values in data to NaNs.

    Keyword arguments:
    mask_i -- Its default is 0. If mask_i is larger than 0, the code prints an
    empty line before printing all the masked values in the data.
    """

    if np.ma.is_masked(var):

        var = np.NaN

        if mask_i == 0:
            print()

        mask_i += 1

        print('detect masked value at '+str(t)+', convert to NaN')

    return var, mask_i


def convert_flag_to_nan(var, flag, t):
    """When the data contains the user-defined flag value.
    Print error message.
    Convert flagged values to NaNs.
    """

    if var == flag:

        print('detect flagged value at '+str(t)+', convert to NaN')
        var = np.NaN

    return var


def check_duplicate_ind_remove(df):
    """When the data contain duplicated values.
    Keep the first entry.
    Remove the rest.
    """

    if df.index.has_duplicates:

        pd.set_option('display.max_rows', None, 'display.max_columns', None)

        dup_ind = df.index.duplicated(keep='first')

        print('')
        print('DETECT '+str(dup_ind.sum())+' ROWS IN DATAFRAME ARE DUPLICATED')
        print('THEY ARE:')
        print(df.iloc[dup_ind])

        print('')
        print('remove duplicated rows listed above')
        df = df[~dup_ind]

    return df


def check_missing_ind_add_nan(df, t_min, t_max, freq):
    """Create an ideal time series with start and end times.
    Match ideal datetime index with input data.
    Detect missing values in input data.
    Replace missing values with NaNs.
    """

    ideal = pd.date_range(start=t_min, end=t_max, freq=str(freq)+'min')
    with_data = ideal.isin(df.index)

    print('')
    print('DETECT '+str(len(ideal[~with_data]))
          + ' ROWS IN DATAFRAME ARE MISSING'
          )
    print('THEY ARE:')
    print(ideal[~with_data].strftime('%Y-%m-%d %H:%M:%S').values)

    ideal_df = pd.DataFrame(data=np.NaN, columns=df.columns+'_i', index=ideal)
    ideal_df.index.name = df.index.name

    new_df = ideal_df.join(df)

    df = new_df[df.columns]

    print('')
    print('assign NaN to missing data at times listed above')

    return df


def verify_data_file_count(df, var, path, freq, updated_len=None):
    """Verify the number of input data files match the user-defined,
    desired data length for analysis.
    Match actual input data frequency with user-defined data frequency.
    Check missing and duplicating values in input data.
    Return unique and continuous data for analysis.
    """

    t_min = df.index.min()
    t_max = df.index.max()

    data_freq = (df.index[1] - t_min).total_seconds() / 60.0

    if data_freq != freq:

        print()
        print('!!!!!!!!!!')
        print('WARNING: DATA FREQUENCY OF FIRST TWO DATA POINTS ')
        print('AND USER-INPUT FREQUENCY DO NOT MATCH')
        print('!!!!!!!!!!')

    # Use data file number in path as a check on data frame length
    data_len_check = len(os.listdir(path))

    # After check_duplicate_ind_remove is called
    if updated_len is not None:
        data_len_check = updated_len

    diff_minute = (t_max - t_min).total_seconds() / 60.0

    print()
    print('read in '+var+' from '+str(t_min)+' to '+str(t_max))
    print('every '+str(freq)+' minutes, total of '+str(data_len_check)
          + ' files'
          )

    desired_len = (diff_minute + freq) / freq

    if data_len_check != desired_len:

        print()
        print('!!!!!!!!!!')
        print('WARNING: '+var+' DATA ENTRY NUMBER ('+str(data_len_check)+')'
              + ' DOES NOT MATCH DESIRED DATA LENGTH ('+str(desired_len)+'),'
              )
        print('WHICH IS DEFINED BY:')
        print('DATA START TIME ('+str(t_min)+'),')
        print('DATA END TIME ('+str(t_max)+'),')
        print('AND USER-INPUT DATA FREQUENCY ('+str(freq)+')')
        print('!!!!!!!!!!')

        # Data frame contains duplicated rows
        if data_len_check > desired_len:

            df = check_duplicate_ind_remove(df)

            print()
            print('verify data again...')
            # Recursion, to verify the data again
            df = verify_data_file_count(df, var, path, freq,
                                        updated_len=len(df)
                                        )

            return df

        # Data frame contains missing rows
        elif data_len_check < desired_len:

            df = check_missing_ind_add_nan(df, t_min, t_max, freq)

            print()
            print('verify data again...')
            # Recursion, to verify the data again
            df = verify_data_file_count(df, var, path, freq,
                                        updated_len=len(df)
                                        )

            return df

    else:

        print()
        print('--- '+var
              + ' dataframe should have unique and continuous data ---')

        return df

# This is a basic parser for sodar NetCDF data.

import os
import pathlib
import datetime
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from qc import check_input_data


class sodar_netcdf:
    """Sodar data class, using data from NetCDF files.
    Each NetCDF file should contain 1 time step of data.
    """

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), str(info['path'])
            )
        self.var = info['var']
        self.target_var = info['target_var']
        self.freq = info['freq']
        self.flag = info['flag']

    def get_ts(self, lev):
        """Get time series at a certain height."""

        df = pd.DataFrame({'t': [], self.target_var: []})

        # To print an empty line before masked value error messages
        mask_i = 0

        for file in os.listdir(self.path):

            data = Dataset(os.path.join(self.path, file), 'r')

            s = '_'.join(file.split('.')[3:5])
            # Sodar data should be in UTC time
            t = datetime.datetime.strptime(s, '%Y%m%d_%H%M%S')
            # If time needs to be offset to UTC time
            # t = datetime.datetime.strptime(s, '%Y%m%d_%H%M%S')
            #     + datetime.timedelta(hours=7)

            height_ind = np.where(data['height'][:].data == lev)[0][0]

            ws = data.variables[self.var][0][height_ind]

            ws, mask_i = check_input_data.convert_mask_to_nan(ws, t, mask_i)
            ws = check_input_data.convert_flag_to_nan(ws, self.flag, t)

            data.close()

            df = df.append([{'t': t, self.target_var: ws}])

        df = df.set_index('t').sort_index()

        df = check_input_data.verify_data_file_count(df, self.target_var,
                                                     self.path, self.freq
                                                     )

        return df

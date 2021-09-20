# This script contains tools for the codebase.

import importlib
import math
import numpy as np


def get_module_class(d, c):
    """Load module m in directory d with the class name c."""

    m = importlib.import_module('.'.join([d, c]))

    return getattr(m, c)


def apply_trans(ts, modlist):
    """Apply a series of transformative modules."""

    for m in modlist:

        ts = m.apply(ts)

    return ts


def append_results(results, base, c, conf):
    """Append results before calculating metrics."""

    results.append({'truth name': base['name'],
                    'model name': c['name'],
                    'path': c['path'],
                    'location': conf['location'],
                    'var': c['var']}
                   )

    return results


def calculate_angle_diff(x_i, y_i):
    """Calculate angle difference between two wind directions.
    Converting wind direction angle into u and v unit vectors,
    to avoid 0-360 degree split.
    It only yields positive angle difference.
    """

    u_x = -math.sin(math.radians(x_i))
    v_x = -math.cos(math.radians(x_i))

    u_y = -math.sin(math.radians(y_i))
    v_y = -math.cos(math.radians(y_i))

    if u_x == u_y and v_x == v_y:
        angle = 0
    else:
        angle = math.degrees(math.acos((u_x*u_y + v_x*v_y)))

    return angle


def get_wd_angle_diff_series(x, y):
    """Convert x and y time series into one series of wind direction
    difference in degrees.
    """

    angle_series = np.empty(len(x))

    for i, (x_i, y_i) in enumerate(zip(x, y)):

        angle_series[i] = calculate_angle_diff(x_i, y_i)

    return angle_series

# This script runs the comparison between timeseries data,
# as specified in config.yaml. This is the main routine for i-validate.
#
# config_test.yaml contains erroneous data that are designed for testing
# this code.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import yaml
import sys
import os
import pathlib
import numpy as np
import pandas as pd

from tools import eval_tools, cal_print_metrics


def compare(config=None):

    config_dir = os.path.join((pathlib.Path(os.getcwd()).parent), 'config')

    if config is None:
        config_file = os.path.join(config_dir, 'config.yaml')
    else:
        config_file = os.path.join(config_dir, config)

    sys.path.append('.')

    conf = yaml.load(open(config_file), Loader=yaml.FullLoader)

    base = conf['base']
    comp = conf['comp']
    p_curve = conf['power_curve']

    print('validation start time:', conf['time']['window']['start'])
    print('validation end time:', conf['time']['window']['end'])
    print('location:', conf['location'])
    print('baseline dataset:', base['name'])
    print('variable:', conf['reference']['var'])

    # Load modules
    metrics = [eval_tools.get_module_class('metrics', m)()
               for m in conf['metrics']]

    crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts')(conf)
    plotting = eval_tools.get_module_class('plotting', 'plot_data')(conf)

    # Data frame containing data at all heights
    all_lev_df = pd.DataFrame()
    all_lev_stat_df = pd.DataFrame()
    all_ramp_ts_df = pd.DataFrame()
    all_ramp_stat_df = pd.DataFrame()

    for lev in conf['levels']['height_agl']:

        # For data storage and metrics computation
        results = []

        print()
        print('######################### height a.g.l.: '+str(lev)
              + ' '+conf['levels']['height_units']
              + ' #########################'
              )
        print()
        print('********** for '+base['name']+': **********')

        # Run __init__
        base['input'] = eval_tools.get_module_class(
            'inputs', base['function'])(base, conf)

        base['data'] = base['input'].get_ts(lev)

        # For each specified comparison dataset
        for ind, c in enumerate(comp):

            print()
            print('********** for '+c['name']+': **********')

            # Run __init__
            c['input'] = eval_tools.get_module_class(
                'inputs', c['function'])(c, conf)

            c['data'] = c['input'].get_ts(lev)

            results = eval_tools.append_results(results, base, c, conf)

            # Crosscheck between datasets
            combine_df = crosscheck_ts.align_time(base, c)

            cal_print_metrics.run(
                combine_df, metrics, results, ind, c, conf, base, lev
                )

            metricstat_dict = {key: results[ind][key]
                               for key in conf['metrics']}
            metricstat_df = pd.DataFrame.from_dict(
                metricstat_dict, orient='index', columns=[c['target_var']]
                )

            metricstat_df.columns = pd.MultiIndex.from_product(
                [[lev], [c['name']], metricstat_df.columns]
                )

            if all_lev_stat_df.empty:
                all_lev_stat_df = all_lev_stat_df.append(metricstat_df)
            else:
                all_lev_stat_df = pd.concat(
                    [all_lev_stat_df, metricstat_df], axis=1
                    )

            plotting.plot_ts_line(combine_df, lev)
            plotting.plot_histogram(combine_df, lev)
            plotting.plot_pair_scatter(combine_df, lev)

            if 'ramps' in conf:

                ramp_data = cal_print_metrics.remove_na(
                    combine_df, ramp_txt=True
                    )

                for ramps in conf['ramps']:

                    r = eval_tools.get_module_class(
                        'ramps', ramps['definition'])(
                            conf, c, ramp_data, ramps)

                    print()
                    print('@@@@@~~ calculating ramp skill scores at '+str(lev)
                          + ' '+conf['levels']['height_units']
                          + ' using definition: '
                          + r.__class__.__name__+' ~~@@@@@')

                    ramp_df = r.get_rampdf()

                    process_ramp = eval_tools.get_module_class(
                        'ramps', 'process_ramp')(ramp_df)

                    ramp_df = process_ramp.add_contingency_table()

                    plot_ramp = eval_tools.get_module_class(
                        'plotting', 'plot_ramp')(
                            ramp_df, combine_df, conf, lev, ramps)

                    # Generating all the ramp texts and plots can take up memory space
                    if 'plotting' in ramps:

                        if ramps['plotting'] is True:
                    
                            plot_ramp.plot_ts_contingency()
                            process_ramp.print_contingency_table()
                            # Print skill scores
                            # process_ramp.cal_print_scores()

                    ramp_summary_df = process_ramp.generate_ramp_summary_df()

                    ramp_summary_df.columns = pd.MultiIndex.from_product(
                        [[lev], [c['name']], [c['target_var']],
                         [r.ramp_nature], [r.get_ramp_method_name()]]
                        )

                    ramp_df.columns = pd.MultiIndex.from_product(
                        [[lev], [c['name']], [c['target_var']],
                         [r.ramp_nature], [r.get_ramp_method_name()], ramp_df.columns]
                        )

                    if all_ramp_stat_df.empty:
                        all_ramp_stat_df = all_ramp_stat_df.append(
                            ramp_summary_df
                            )
                        all_ramp_ts_df = all_ramp_ts_df.append(
                            ramp_df
                            )
                    else:
                        all_ramp_stat_df = pd.concat(
                            [all_ramp_stat_df, ramp_summary_df], axis=1
                            )
                        all_ramp_ts_df = pd.concat(
                            [all_ramp_ts_df, ramp_df], axis=1
                            )

            combine_df.columns = pd.MultiIndex.from_product(
                [[lev], [c['name']], combine_df.columns]
                )

            if all_lev_df.empty:
                all_lev_df = all_lev_df.append(combine_df)
            else:
                all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)

    if 'output' in conf and conf['output']['writing'] is True:

        output_path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), conf['output']['path']
            )

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if conf['output']['format'] == 'csv':

            all_lev_df.to_csv(
                os.path.join(output_path,
                             'ts_'+conf['output']['org']+'.csv')
                )
            all_lev_stat_df.to_csv(
                os.path.join(output_path,
                             'metrics_'+conf['output']['org']+'.csv')
                )

            if 'ramps' in conf:

                all_ramp_stat_df.to_csv(
                    os.path.join(output_path,
                                 'ramp_'+conf['output']['org']+'.csv')
                    )
                all_ramp_ts_df.to_csv(
                    os.path.join(output_path,
                                 'ramp_ts_'+conf['output']['org']+'.csv')
                    )

    pc_results = []

    # For power curve
    for ind, c in enumerate(comp):

        # If both variables are wind speeds
        # and hub height exists in user-defined validation levels
        if (
            base['nature'] == 'ws' and c['nature'] == 'ws'
            and p_curve['hub_height'] in all_lev_df.columns.get_level_values(0)
        ):

            print()
            print('######################### deriving wind power at '
                  + str(p_curve['hub_height'])
                  + ' '+conf['levels']['height_units']
                  + ' #########################')
            print()
            print('use power curve: '+p_curve['file'])

            hh = p_curve['hub_height']

            hhws_df = all_lev_df.xs([hh, c['name']], level=0, axis=1)

            pc_csv = eval_tools.get_module_class(
                'inputs', p_curve['function'])(
                p_curve['path'], p_curve['file'], p_curve['ws'],
                p_curve['power'], hhws_df, hh, conf
                )

            power_df = pc_csv.get_power()

            pc_results = eval_tools.append_results(pc_results, base, c, conf)

            cal_print_metrics.run(
                power_df, metrics, pc_results, ind, c, conf, base, hh
                )

            # Plot simulated power curves, not extremely useful
            # pc_csv.plot_pc()
            
            pc_csv.plot_power_ts()

            pc_csv.plot_power_scatter()

            # Generate derived power output file
            if ('output_path' in p_curve) and ('wt_num' in p_curve):

                # Convert to MW for wind farm
                power_df = power_df * p_curve['wt_num'] / 1e3
                # print(power_df)
                # print(c['name'])

                # c should has 1 element
                col = [s for s in power_df.columns if c['name'] in s][0]
                # print(col)
                # print(col)

                new_col = 'power_'+str(p_curve['hub_height']).replace('.', '-')+conf['levels']['height_units']
                # print(new_col)

                # power_df[col]

                # print(power_df.rename({col: new_col}, axis=1))

                power_df.rename(columns={col: new_col}, inplace=True)

                # 'power_78-25m'

                power_df[new_col].to_csv(
                    os.path.join(output_path, p_curve['output_path'], 
                    'derived_power_'+c['name']+'.csv')
                    )

                # power_df[col].to_csv(
                #     os.path.join(output_path, 
                #     'test.csv')
                #     )

                # power_df.columns = pd.MultiIndex.from_product(
                # [[lev], [c['name']], combine_df.columns]
                # )

        else:

            print()
            print('not deriving power for '+c['name']+',')
            print('either baseline and compare data are not wind speed,\n'
                  + 'or hub height does not exist in validation data,\n'
                  + 'hence power curve is not derived'
                  )

# Ramp processing
# Derive 2x2 contingency table based on baseline vs comparison accuracy
# Calculate different skill scores according to the contingency table
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class process_ramp:
    """Class to process ramp results."""

    def __init__(self, ramp_df):

        self.df = ramp_df

    def add_contingency_table(self):
        """Categorize ramp forecast accuracy between baseline ramps
        and comparison ramps based on a 2x2 contingency table.
        """

        false_col = np.zeros(len(self.df), dtype=bool)
        self.df['true_positive'] = false_col
        self.df['false_positive'] = false_col
        self.df['false_negative'] = false_col
        self.df['true_negative'] = false_col

        # self.df.loc[((self.df['base_ramp'] != 0)
        #             & (self.df['comp_ramp'] != 0)),
        #             ['true_positive']] = True
        # self.df.loc[((self.df['base_ramp'] == 0)
        #             & (self.df['comp_ramp'] != 0)),
        #             ['false_positive']] = True
        # self.df.loc[((self.df['base_ramp'] != 0)
        #             & (self.df['comp_ramp'] == 0)),
        #             ['false_negative']] = True
        # self.df.loc[((self.df['base_ramp'] == 0)
        #             & (self.df['comp_ramp'] == 0)),
        #             ['true_negative']] = True

        self.df.loc[((self.df['base_ramp'] == 1)
                    & (self.df['comp_ramp'] == 1)),
                    ['true_positive']] = True
        self.df.loc[((self.df['base_ramp'] == 0)
                    & (self.df['comp_ramp'] == 1)),
                    ['false_positive']] = True
        self.df.loc[((self.df['base_ramp'] == 1)
                    & (self.df['comp_ramp'] == 0)),
                    ['false_negative']] = True
        self.df.loc[((self.df['base_ramp'] == 0)
                    & (self.df['comp_ramp'] == 0)),
                    ['true_negative']] = True

        # Confirm that only 1 of 4 categories contains a True signal
        # for each time step
        for i, row in self.df.iterrows():
            assert np.sum([row['true_positive'], row['false_positive'],
                          row['false_negative'], row['true_negative']]) == 1

        self.true_pos = self.df['true_positive'].sum()
        self.false_pos = self.df['false_positive'].sum()
        self.false_neg = self.df['false_negative'].sum()
        self.true_neg = self.df['true_negative'].sum()

        assert self.true_pos+self.false_pos\
               + self.false_neg+self.true_neg == len(self.df)

        return self.df

    def print_contingency_table(self):
        """Print 2x2 contingency table via pandas."""

        data = [
            ['|', 'true positive: '+str(self.true_pos),
             '|', 'false positive: '+str(self.false_pos),
             '|', self.true_pos+self.false_pos],
            ['|', 'false negative: '+str(self.false_neg),
             '|', 'true negative: '+str(self.true_neg),
             '|', self.false_neg+self.true_neg],
            ['|', self.true_pos+self.false_neg, '|',
             self.false_pos+self.true_neg,
             '|', len(self.df)]
            ]

        print_df = pd.DataFrame(
            data,
            columns=['|', 'Benchmark: ramps', '|', 'Benchmark: no ramps',
                     '|', 'Total'],
            index=['Comparison: ramps', 'Comparison: no ramps', 'Total']
            )

        print('2x2 contingency table:')
        print(print_df)
        print()

    def generate_ramp_summary_df(self):
        """Generate data frame of contingency table."""

        data = {
            'time_sample': len(self.df),
            'base_ramp': self.df['base_ramp'].sum(),
            'comp_ramp': self.df['comp_ramp'].sum(),
            'true_positive': self.true_pos,
            'false_positive': self.false_pos,
            'false_negative': self.false_neg,
            'true_negative': self.true_neg,
            'probability_of_detection': self.cal_pod(),
            'critical_success_index': self.cal_csi(),
            'frequency_bias_score': self.cal_fbias(),
            'false_alarm_rate': self.cal_farate(),
            'forecast_accuracy': self.cal_fa(),
            'peirces_skill_score': self.cal_pss(),
            'symmetric_extreme_dependency_score': self.cal_seds()
            }

        return pd.DataFrame.from_dict(data, orient='index')

    def cal_pod(self, msg=False):
        """Probability of detection."""

        # To avoid runtime warning
        if (self.true_pos+self.false_neg) == 0:
            pod = np.nan
        else:
            pod = self.true_pos/(self.true_pos+self.false_neg)

        if msg is True:
            print('Probability of detection, or Ramp capture, or Hit '
                  + 'percentage (the fraction of ')
            print('observed ramp events that are actually forecasted): '
                  + str(np.round(pod, 3)))
            print()

        return pod

    def cal_csi(self, msg=False):
        """Critical success index."""

        if (self.true_pos+self.false_pos+self.false_neg) == 0:
            csi = np.nan
        else:
            csi = self.true_pos/(self.true_pos+self.false_pos+self.false_neg)

        if msg is True:
            print('Critical success index (the fraction of observed and/or '
                  + 'forecasted events ')
            print('that are correctly predicted), where 1 is perfect '
                  + 'prediction: '+str(np.round(csi, 3)))
            print()

        return csi

    def cal_fbias(self, msg=False):
        """Frequency bias score."""

        if (self.true_pos+self.false_neg) == 0:
            fbias = np.nan
        else:
            fbias = (self.true_pos+self.false_pos)/(self.true_pos+self.false_neg)

        if msg is True:
            print('Frequency bias score (the ratio of the frequency of '
                  + 'forecasted ramp events to the ')
            print('frequency of observed ramp events), where a value < 1 '
                  + 'represents the system ')
            print('tends to underforecast and a value > 1 represents '
                  + 'the system tends to ')
            print('overforecast: '+str(np.round(fbias, 3)))
            print()

        return fbias

    def cal_farate(self, msg=False):
        """False alarm rate."""

        if (self.true_neg+self.false_pos) == 0:
            farate = np.nan
        else:
            farate = self.false_pos/(self.true_neg+self.false_pos)

        if msg is True:
            print('False alarm rate (the fraction of predicted ramp events '
                  + 'that did not occur): '+str(np.round(farate, 3)))
            print()

        return farate

    def cal_fa(self, msg=False):
        """Forecast accuracy."""

        if (self.true_pos+self.false_pos) == 0:
            fa = np.nan
        else:
            fa = self.true_pos/(self.true_pos+self.false_pos)

        if msg is True:
            print('Forecast accuracy, or Success ratio (the fraction of '
                  + 'predicted YES events ')
            print('that occurred): '+str(np.round(fa, 3)))

        return fa

    def cal_pss(self, msg=False):
        """Peirce's skill score."""

        # pss = ((self.true_pos*self.true_neg)
        #        - (self.false_pos*self.false_neg))\
        #     / ((self.true_pos+self.false_neg)
        #        * (self.false_pos+self.true_neg))

        pod = self.cal_pod()
        farate = self.cal_farate()

        if (np.isnan(pod)) or (np.isnan(farate)):
            pss = np.nan
        else:
            pss = pod-farate

        return pss

    def cal_seds(self, msg=False):
        """Symmetric extreme dependency score."""

        if self.true_pos == 0:
            seds = np.nan
        else: 
            n = len(self.df)
            seds = ((np.log((self.true_pos+self.false_pos)/n)\
                     +np.log((self.true_pos+self.false_neg)/n))\
                    / np.log(self.true_pos/n)) - 1

        return seds

    def cal_print_scores(self):
        """Calculate and print different ramp skill scores."""

        print('ramp skill scores:')
        print()
        self.cal_pod(msg=True)
        self.cal_csi(msg=True)
        self.cal_fbias(msg=True)
        self.cal_farate(msg=True)
        self.cal_fa(msg=True)
        self.cal_pss(msg=True)
        self.cal_seds(msg=True)

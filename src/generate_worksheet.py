import pandas as pd
import re
import os
from src.read_worksheet import read_worksheet as RW

class generate_worksheet(RW):
    '''Generate Worksheet
    '''
    def __init__(self, fname):
        super().__init__(fname=fname)

        self.df_all_labeled = [None for i in range(5)]
        self.df_concat = None
        self.df_oos = None
        self.df_categorical = None

    def label_worksheet(self):
        for i, df in enumerate(self.df_all):

            tmp_df = pd.DataFrame(columns=list(df.columns) + ['Category'])

            for l, item in self.criteria.items():
                if l == 'exclude':
                    continue

                tmp_inner = df.query('Amount < 0')
                tmp_inner = tmp_inner[tmp_inner.Description.isin(item)]
                tmp_inner['Category'] = l
                tmp_df = pd.concat([tmp_df, tmp_inner])

            self.df_all_labeled[i] = tmp_df

    def combine_worksheet(self, to_file=False):
        self.df_concat = self.df_all_labeled[0]
        self.df_concat = pd.concat([self.df_concat, self.df_all_labeled[1]])
        self.df_concat = pd.concat([self.df_concat, self.df_all_labeled[2]])
        
        self.oos_worksheet()
        self.df_concat = pd.concat([self.df_concat, self.df_oos])

        self.df_concat.sort_values(['Category'], inplace=True)
        # self.df_concat['Posted Date'] = self.df_concat['Posted Date'].apply(lambda x: x.date())

        if to_file:
            self.df_concat.to_excel(f'{self.year}_combined_loss.xlsx', index=False)

    def categorical_worksheet(self, to_file=False):
        self.df_categorical = self.df_concat.groupby('Category')[['Amount']].sum();
        self.df_categorical.Amount = abs(self.df_categorical.Amount)
        self.df_categorical.sort_index(inplace=True)

        if to_file:
            self.df_categorical.to_excel(f'{self.year}_categorical_loss.xlsx')

    def oos_worksheet(self):
        _folder_path = os.path.join('tax', self.year, 'out-of-scope')

        tmp_df = pd.DataFrame(columns=self.df_all_labeled[0].columns)

        flist = os.listdir(_folder_path)
        for fn in flist:
            _file_path = os.path.join(_folder_path, fn)
            tmp_df = pd.concat([tmp_df, pd.read_excel(_file_path)])

        self.df_oos = tmp_df
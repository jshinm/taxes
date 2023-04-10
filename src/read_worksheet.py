import pandas as pd
import re
import os
import warnings

from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

from src.load_criterion import load_criterion as LC

class read_worksheet(LC):
    '''Read Worksheet
    '''
    def __init__(self, fname):
        super().__init__(fname=fname)
        #TODO: fix all these
        self.load_all()

        self.df_check = pd.read_excel(self._file_path, sheet_name=1)
        self.df_cc0 = pd.read_excel(self._file_path, sheet_name=2)
        self.df_cc1 = pd.read_excel(self._file_path, sheet_name=3)
        self.df_mr = pd.read_excel(self._file_path, sheet_name=4)
        self.df_amex = pd.read_excel(self._file_path, sheet_name=5)

        label1 = ['Date', 'Description', 'Amount']
        #TODO: remove label2
        label2 = ['Posted Date', 'Description', 'Amount']

        self.df_check = self.df_check[label1]
        self.df_cc0 = self.df_cc0[label1]
        self.df_cc1 = self.df_cc1[label1]
        self.df_mr = self.df_mr[label1]
        self.df_amex = self.df_amex[label1]

        self.df_all = [self.df_check, self.df_cc0, \
                       self.df_cc1, self.df_mr, \
                       self.df_amex]

        self.criteria = self.criteria

        self.year = re.findall(pattern='[0-9]{4}', string=fname)[0]

        self.profit = None
        self.loss = None

    def preprocess(self, df_num=0, filter=None, as_file=False):
        #TODO: fix all these manual sheet names
        self.sheet_name = ['check', 'cc0', 'cc1', 'mr', 'amex'][df_num]
        df = self.df_all[df_num]
        df['Account'] = self.sheet_name

        self.profit = df.query('Amount > 0')
        self.loss = df.query('Amount < 0')

        if as_file:
            self.profit.to_excel(f'tax/{self.year}/profit/profit_{self.sheet_name}.xlsx', index=False)
            self.loss.to_excel(f'tax/{self.year}/loss/loss_{self.sheet_name}.xlsx', index=False)

    def exclude_all(self, include_retail=True, to_file=False):
        tmp = []
        if to_file:
            for _, lst in self.criteria.items():
                tmp += lst

            if include_retail:
                self.read_costco()
                self.read_amazon()
                
                tmp += self.costco
                tmp += self.amazon
                
                self._misc_save(category=self.costco, fname=f'loss_{self.sheet_name}_costco.xlsx')
                self._misc_save(category=self.amazon, fname=f'loss_{self.sheet_name}_amazon.xlsx')

            folderPath = os.path.join('tax', self.year, 'uncategorized')
            filePath = f'loss_{self.sheet_name}_exclude_all.xlsx'
            self.loss[~self.loss.Description.isin(tmp)].to_excel(os.path.join(folderPath, filePath), index=False)

    def _misc_save(self, category, fname):
        folderPath = os.path.join('tax', self.year, 'out-of-scope')
        tmp_df = self.loss[self.loss.Description.isin(category)]
        tmp_df['Category'] = 'operation'
        tmp_df.to_excel(os.path.join(folderPath,fname), index=False)

    def read_costco(self):
        self.costco = [i for i in self.loss.Description if re.findall(pattern='costco', string=str(i).lower())]

    def read_amazon(self):
        self.amazon = [i for i in self.loss.Description if re.findall(pattern='amzn', string=str(i).lower())]
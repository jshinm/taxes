import pandas as pd
import re
from src.load_criterion import load_criterion as LC

class read_worksheet:
    '''Read Worksheet
    '''
    def __init__(self, fname):
        lc = LC(fname=fname)
        self.lc = lc.load_all()

        self.df_check = pd.read_excel(lc._file_path, sheet_name=1)
        self.df_cc0 = pd.read_excel(lc._file_path, sheet_name=2)
        self.df_cc1 = pd.read_excel(lc._file_path, sheet_name=3)

        self.criteria = lc.criteria

        self.profit = None
        self.loss = None

    def preprocess(self, df_num=0, filter=None, as_file=False):
        self.sheet_name = ['check', 'cc0', 'cc1'][df_num]
        df = [self.df_check, self.df_cc0, self.df_cc1][df_num]

        self.profit = df.query('Amount > 0')
        self.loss = df.query('Amount < 0')

        if as_file:
            self.profit.to_excel(f'profit_{self.sheet_name}.xlsx', index=False)
            self.loss.to_excel(f'loss_{self.sheet_name}.xlsx', index=False)

    def exclude_all(self, include_retail=True):
        tmp = []
        for _, lst in self.criteria.items():
            tmp += lst

        if include_retail:
            self.read_costco()
            self.read_amazon()
            tmp += self.costco
            tmp += self.amazon
            self.loss[self.loss.Description.isin(self.costco)].to_excel(f'loss_{self.sheet_name}_costco.xlsx', index=False)
            self.loss[self.loss.Description.isin(self.amazon)].to_excel(f'loss_{self.sheet_name}_amazon.xlsx', index=False)

        self.loss[~self.loss.Description.isin(tmp)].to_excel(f'loss_{self.sheet_name}_exclude_all.xlsx', index=False)

    def read_costco(self):
        self.costco = [i for i in self.loss.Description if re.findall(pattern='costco', string=str(i).lower())]

    def read_amazon(self):
        self.amazon = [i for i in self.loss.Description if re.findall(pattern='amzn', string=str(i).lower())]
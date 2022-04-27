import io
import re
import os
import yaml

class load_criterion:
    '''Load Criterion
    '''
    def __init__(self, fname):

        with open('filepath.yml', 'r') as f:
            self._folder_path = yaml.safe_load(f)['folder_path']
        
        self._file_path = os.path.join(self._folder_path, fname)

        self._fname = fname
        self.criteria = dict()

    def load_all(self):
        flist = os.listdir('criteria')
        for fn in flist:
            with open(f'criteria/{fn}', 'r', encoding='utf-8') as f:
                tmp = fn[:fn.find('.')]
                try:
                    self.criteria[tmp] = f.readlines()
                    self.criteria[tmp] = [i.replace('\n', '') for i in self.criteria[tmp]]
                except Exception as e:
                    print(e)

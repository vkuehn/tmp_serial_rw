import datetime


class Logger:
    def __init__(self, node_name='logger'):
        self.node_name = node_name
        
    def log(self, text, name=''):
        if name == '':
            name = self.node_name
        _date = str(datetime.datetime.now())
        print('[' + _date + '][' + name + ']' + str(text))

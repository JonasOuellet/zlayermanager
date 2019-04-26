import os
import json
import sys


if not getattr(sys, 'frozen', False):
    ZBRUSH_PATH = r"C:\Program Files\Pixologic\ZBrush 2018 FL\ZBrush.exe"
else:
    # find path
    pass

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'zlm.txt')


class ZlmSettings(object):
    _instance = None
    exclude_attr = set(['bigData'])

    def __init__(self, auto_load=True):
        self.working_folder = os.path.join(self.getsettingfolder(), 'files')
        self.communication_port = 6008

        self.maya_auto_import = True
        self.maya_communication_port = 6009

        self.export_format = '.obj'

        self.bigData = {}

        if auto_load:
            self.load()

    @staticmethod
    def getsettingfolder():
        folder = os.path.expanduser(os.path.join('~', 'zLayerManager'))
        if not os.path.exists(folder):
            os.makedirs(folder)

        return folder

    @staticmethod
    def getsettingfile():
        return os.path.join(ZlmSettings.getsettingfolder(), 'settings.json')

    def save_to_file(self):
        outdict = dict(vars(self))
        for attr in self.exclude_attr:
            outdict.pop(attr)

        for attr in self.bigData:
            outdict[attr] = self.bigData[attr]

        with open(self.getsettingfile(), mode='w') as f:
            json.dump(outdict, f, indent=4)

    def load(self):
        try:
            with open(self.getsettingfile(), mode='r') as f:
                outdict = json.load(f)

                for attr in vars(self):
                    if attr not in self.exclude_attr:
                        setattr(self, attr, outdict.pop(attr, getattr(self, attr)))

                for key, value in outdict.items():
                    self.bigData[key] = value

        except Exception as e:
            pass

    @staticmethod
    def instance():
        if not ZlmSettings._instance:
            ZlmSettings._instance = ZlmSettings()
        return ZlmSettings._instance

    def get(self, key, defaultValue=None):
        if key not in self.bigData:
            self.bigData[key] = defaultValue

        if isinstance(defaultValue, dict):
            for k, value in defaultValue.items():
                if k not in self.bigData[key]:
                    self.bigData[key][k] = value

        return self.bigData[key]

    def set(self, key, value):
        self.bigData[key] = value

    def __getitem__(self, index):
        try:
            return self.bigData[index]
        except KeyError as e:
            return None

    def __setitem__(self, key, value):
        self.bigData[key] = value

    def get_export_folder(self):
        folder = os.path.join(self.working_folder, 'export')
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return folder

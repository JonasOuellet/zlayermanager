import os
import json
import sys


class ZlmSettings(object):
    _instance = None
    exclude_attr = set(['bigData'])

    def __init__(self, auto_load=True):
        self.working_folder = os.path.join(self.getsettingfolder(), 'files')
        self.communication_port = 6008

        self.send_after_export = False
        self.current_dcc = 'Maya'
        self.dcc_settings = {
            'Maya': {
                'port': 6009,
                'format': '.obj'
            }
        }

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

    def _recursive_update(self, _dict, to_add):
        for k, value in to_add.items():
            if k not in _dict:
                _dict[k] = value
            elif isinstance(value, dict):
                self._recursive_update(_dict[k], value)

    def get(self, key, defaultValue=None):
        if key not in self.bigData:
            self.bigData[key] = defaultValue

        if isinstance(defaultValue, dict):
            self._recursive_update(self.bigData[key], defaultValue)

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

    def get_import_folder(self):
        folder = os.path.join(self.working_folder, 'import')
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return folder

    def get_current_dcc_port(self):
        try:
            return self.dcc_settings[self.current_dcc]['port']
        except:
            pass
        return None

    def get_current_dcc_format(self):
        try:
            return self.dcc_settings[self.current_dcc]['format']
        except:
            pass
        # default format
        return '.obj'

    def get_port_for_dcc(self, dcc):
        try:
            return self.dcc_settings[dcc]['port']
        except:
            raise Exception('Could not find port for software "{}".  Make sure this software is properly set in settings.')


def instance():
    return ZlmSettings.instance()

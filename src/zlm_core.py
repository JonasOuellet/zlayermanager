from collections import OrderedDict
from enum import IntEnum
import copy
import subprocess
import os
import sys
import json

from zlm_settings import ZBURSH_PATH, SCRIPT_PATH

ZLM_OP_RENAME = 0
ZLM_OP_MODE = 1
ZLM_OP_CREATE = 2


class ZlmCreateOp(object):
    def __init__(self, name):
        self.name = name


class ZlmRenameOp(object):
    def __init__(self, basename, newname):
        self.op = ZLM_OP_RENAME
        self.basename = basename
        self.newname = newname


class ZlmLayerOp(object):
    def __init__(self):
        self.instances = {}
        self.instances_list = []

        self.currentRecording = None

        # self.is_recording = False
        # self.layer_record_start = None
        # self.layer_record_end = None

        self.ops = []

    def start_recording(self):
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False

    def send_to_zbrush(self):
        pass

    def add_layer(self, layer):
        # if self.is_recording:
        #     pass
        l = self.instances.get(layer.name, [])
        l.append(layer)
        self.instances[layer.name] = l
        self.instances_list.append(layer)

    def clear(self):
        self.instances.clear()
        self.instances_list.clear()


_zOp = ZlmLayerOp()


class ZlmLayerMode(IntEnum):
    off = 0
    record = 1
    active = 2


class ZlmLayer(object):
    def __init__(self, name, intensity, mode, index):
        super(ZlmLayer, self).__init__()
        self.name = name
        self.intensity = intensity
        self.mode = mode
        self.index = index

        _zOp.add_layer(self)

    # @property
    # def name(self):
    #     return self._name

    # @name.setter
    # def name(self, value):
    #     if ZlmLayer.layerOp.recording:

    #     self._name = value

    # @property
    # def mode(self):
    #     return self._mode

    # @mode.setter
    # def mode(self, value):
    #     if value = ZlmLayerMode.record:
    #         if _zOp.currentRecording:
    #             _zOp.currentRecording.mode = ZlmLayerMode.active
    #         _zOp.currentRecording = self
    #     self._mode = value

    @staticmethod
    def from_line(line, line_index):
        line = line.strip()
        start = line.find("\"")
        end = line.find("\"", start+1)

        splitted = line[end+1:].strip().split(' ')
        return ZlmLayer(line[start+1: end], float(splitted[0]), int(splitted[1]), line_index)

    @staticmethod
    def start_recording(self):
        ZlmLayer.layerOp.start_recording()

    @staticmethod
    def stop_recording(self):
        pass


class ZlmSubTool(object):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    @staticmethod
    def from_line(line):
        line = line.strip()
        start = line.find("\"")
        end = line.find("\"", start+1)
        splitted = line[end+1:].strip()
        return ZlmSubTool(line[start+1: end], int(splitted))


def parse_layer_file(file_path):
    """Parse the given layers file and return the list of layer

    Args:
        file_path (str): The file path

    Returns: (layersList, subtoolName)
    """
    _zOp.clear()
    subTool = None

    with open(file_path, mode='r') as f:
        lines = f.readlines()
        # last line is for subtools
        for x, line in enumerate(lines[:-1]):
            layer = ZlmLayer.from_line(line, x)
        subTool = ZlmSubTool.from_line(lines[-1])

    return _zOp.instances_list, subTool


def get_preset_folders():
    """ Look for preset folder
    1. With the executable
    2. In the user
    """

    out = {
        'app': None,
        'user': None
    }

    if getattr(sys, 'frozen', False):
        root = sys.executable
    else:
        root = __file__

    directory = os.path.join(os.path.dirname(root), 'presets')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    out['app'] = directory

    directory = os.path.expanduser(os.path.join('~', 'zLayerManager', 'presets'))
    if not os.path.isdir(directory):
        os.makedirs(directory)
    out['user'] = directory

    return out


def get_preset_file():
    folders = get_preset_folders()
    out = {}
    for key, value in folders.items():
        if value:
            out[key] = tuple(os.path.join(value, f) for f in os.listdir(value) if '.json' in f)
        else:
            out[key] = ()
    return out


def load_presets():
    preset_files = get_preset_file()
    out = {}
    for key, value in preset_files.items():
        out[key] = {}
        for f in value:
            filename = os.path.basename(f).split('.')[0]
            with open(f, mode='r') as filobj:
                out[key][filename] = json.load(filobj)
    return out


def get_layers_as_preset():
    out = {
        'active': [],
        'record': None
    }

    for layer in _zOp.instances_list:
        if layer.mode == 1:  # or layer.intensity != 1.0:
            out['record'] = {
                'name': layer.name,
                'index': layer.index
            }
        elif layer.mode == 2:
            curLayer = {
                'name': layer.name,
                'index': layer.index,
                'intensity': layer.intensity,
            }
            out['active'].append(curLayer)

    return out

def apply_preset(preset):
    # loop through all layers and apply default value

    for layer in _zOp.instances_list:
        layer.intensity = 1.0
        layer.mode = 0

    for layer in preset['active']:
        layers = _zOp.instances.get(layer['name'], None)
        if layers:
            if len(layers) > 1:
                # check for index in the array of layer with the same name
                for l in layers:
                    if l.index == layer['index']:
                        cl = l
                        break
                else:
                    # Maybe just skip ?
                    # cl = layers[0]
                    continue
            else:
                cl = layers[0]

            cl.mode = 2
            cl.intensity = layer['intensity']

    if preset['record']:
        layers = _zOp.instances.get(preset['record']['name'], None)
        if layers:
            if len(layers) > 1:
                # check for index in the array of layer with the same name
                for l in layers:
                    if l.index == layer['index']:
                        cl = l
                        break
                else:
                    # Maybe just skip ?
                    # cl = layers[0]
                    return
            else:
                cl = layers[0]

            cl.mode = 1


def save_layers_preset(name, data):
    folder = get_preset_folders()
    filepath = os.path.join(folder['user'], name + '.json')

    with open(filepath, mode='w') as f:
        json.dump(data, f, indent=4)


startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def send_to_zbrush():
    with open(SCRIPT_PATH, mode='w') as f:
        f.write(SET_LAYER_FUNC)
        f.write(RECT_FUNC)
        f.write('[IShowActions, 0]')
        f.write('\n[IFreeze,\n')
        f.write('[RoutineCall, zlmDeactivateRec]\n')

        recording_layer = None
        layerCount = len(_zOp.instances_list) - 1
        for x in range(layerCount, -1, -1):
            l = _zOp.instances_list[x]
            if l.mode == ZlmLayerMode.record:
                if not recording_layer:
                    recording_layer = l
                    continue
                else:
                    l, recording_layer = (recording_layer, l)
                    
            f.write('[RoutineCall,zlmSetLayerMode,"{}",{},{},{}]\n'.format(l.name, layerCount-x, l.mode, l.intensity))

        if recording_layer:
            f.write('[RoutineCall,zlmSetLayerMode,"{}",{},{},{}]\n'.format(recording_layer.name, 
                layerCount-recording_layer.index, recording_layer.mode, 1.0))

        f.write(']')
        
    subprocess.call([ZBURSH_PATH, SCRIPT_PATH])


def send_intensity(layers=None, intensity=1.0):
    if layers is None:
        layers = _zOp.instances_list

    layerCount = len(_zOp.instances_list) - 1
    with open(SCRIPT_PATH, mode='w') as f:
        f.write(SET_INTENSITY_FUNC)
        f.write('[IShowActions, 0]')
        f.write('\n[IFreeze,\n')

        for layer in layers:
            f.write('[RoutineCall,zlmIntensity,{},{},{}]\n'.format(layer.name, layerCount-layer.index, intensity))
    
        f.write(']')
    subprocess.call([ZBURSH_PATH, SCRIPT_PATH])


def export_layers(output_folder, output_format='.obj', layers=None):
    if layers is None:
        layers = _zOp.instances_list

    layerCount = len(_zOp.instances_list) - 1

    with open(SCRIPT_PATH, mode='w') as f:
        f.write(RECT_FUNC)
        f.write(SET_LAYER_FUNC)
        f.write(EXPORT_LAYER_FUNC)
        f.write(SUBDIV_ZERO_)
        f.write('[IShowActions, 0]')
        f.write('\n[IFreeze,\n')

        f.write('[RoutineCall, zlmDeactivateRec]\n')
        
        # f.write('[VarSet, zlmOpath, "{}"]'.format(output_folder))

        layerCount = len(_zOp.instances_list) - 1
        # Deactive any active layers
        for x, l in enumerate(_zOp.instances_list):
            f.write('[RoutineCall,zlmSetLayerMode,"{}",{},{},{}]\n'.format(l.name, layerCount-x, l.mode, 1.0))

        # export layers
        for l in layers:
            # path = '[StrMerge, #zlmOpath,"{}"]'.format(l.name + output_format)
            path = os.path.join(output_folder, l.name + output_format)
            f.write('[RoutineCall,zlmExportLayer,"{}",{},"{}"]\n'.format(l.name, layerCount-l.index, path))

        # restore layer back
        recording_layer = None
        for x in range(layerCount, -1, -1):
            l = _zOp.instances_list[x]
            if l.mode == ZlmLayerMode.record:
                if not recording_layer:
                    recording_layer = l
                    continue
                else:
                    l, recording_layer = (recording_layer, l)

            f.write('[RoutineCall,zlmSetLayerMode,"{}",{},{},{}]\n'.format(l.name, layerCount-x, l.mode, l.intensity))

        if recording_layer:
            f.write('[RoutineCall,zlmSetLayerMode,"{}",{},{},{}]\n'.format(recording_layer.name, 
                    layerCount-recording_layer.index, recording_layer.mode, 1.0))
            
        f.write(SUBDIV_RESTORE_)
        f.write(']')
    
    subprocess.call([ZBURSH_PATH, SCRIPT_PATH])


RECT_FUNC = '''[RoutineDef,zlmDeactivateRec,[VarSet,curLayerName,[IGetTitle,"Tool:Layers:Layer Intensity"]][If, [IsEnabled,Tool:Layers:SelectDown],[IPress, Tool:Layers:SelectDown]
,[ISet, "Tool:Layers:Layers Scrollbar", 0, 0]]
[If, [IsEnabled, Tool:Layers:SelectUp],[IPress, Tool:Layers:SelectUp][IPress, Tool:Layers:SelectUp]]
[VarSet, curLayerPath, [StrMerge, "Tool:Layers:", #curLayerName]]
[VarSet, mode, [IModGet, curLayerPath]]
[If, #mode == 1,
[VarSet, wid, [IWidth,curLayerPath]]
[IClick, curLayerPath, wid-10, 5]]]'''
SET_LAYER_FUNC = '''[RoutineDef, zlmSetLayerMode,
    [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
    [VarSet, layerPath, [StrMerge, "Tool:Layers:", #layerName]]

    [If, mode == 2,
            [ISet, layerPath, intensity]
    ]

    [VarSet, curMode, [IModGet, layerPath]]
    
    [If, curMode != mode,
        [VarSet, wid, [IWidth, layerPath]]
        [If, mode == 1,
            [IClick, layerPath, wid-20, 5]
        ]
        [If, ((mode == 0) || (mode == 2)),
            [IClick, layerPath, wid-5, 5]
        ]
    ]
, layerName, index, mode, intensity]
'''

SET_INTENSITY_FUNC = '''[RoutineDef, zlmIntensity,
    [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
    [ISet, [StrMerge, "Tool:Layers:", #layerName], intensity]
, layerName, index, intensity]
'''

EXPORT_LAYER_FUNC = '''[RoutineDef, zlmExportLayer,
    [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
    [VarSet, layerPath, [StrMerge, "Tool:Layers:", #layerName]]
    [VarSet, wid, [IWidth, layerPath]]
    [ISet, layerPath, 1.0]

    [If, [IModGet, layerPath] == 0,
        [IClick, layerPath, wid-5, 5]
    ]
    [FileNameSetNext, #savePath]
    [IKeyPress, 13, [IPress, TOOL:Export:Export ]]

    [IClick, layerPath, wid-5, 5]

, layerName /*string*/, index /*number*/, savePath /*string*/]'''


SUBDIV_ZERO_ = '''[VarSet, subLevel, [IGet, "Tool:Geometry:SDiv"]]
[ISet, "Tool:Geometry:SDiv", 0, 0]
'''

SUBDIV_RESTORE_ = '[ISet, "Tool:Geometry:SDiv", #subLevel, 0]'

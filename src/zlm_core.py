from enum import IntEnum
import os
import sys
import json
import re

from typing import List

from zlm_settings import ZlmSettings

invalid_char_re = re.compile('[^A-Za-z0-9_]')
valid_name_re = "[A-Za-z0-9_]{0,15}"
max_name_len = 15


class ZlmLayerMode(IntEnum):
    off = 0
    record = 1
    active = 2


class ZlmSubTool(object):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    @staticmethod
    def from_line(line, index):
        line = line.strip()
        start = line.find("\"") + 1
        end = line.find("\"", start)
        name = line[start: end]
        if name.endswith('.'):
            name = name[:-1]
        return ZlmSubTool(name, index)


class ZlmLayer(object):
    def __init__(self, name, intensity, mode, index, master=None):
        super(ZlmLayer, self).__init__()
        self.master = master
        self._mode = 0
        self.name = name
        self.intensity = intensity
        self.mode = mode
        self.index = index

    @property
    def mode(self):
        return int(self._mode)

    @mode.setter
    def mode(self, value):
        if value == ZlmLayerMode.record:
            if self.master:
                if self.master.recording_layer:
                    self.master.recording_layer._mode = ZlmLayerMode.active
                self.master.recording_layer = self
        else:
            if self.master:
                if self.master.recording_layer == self:
                    self.master.recording_layer = None
        self._mode = value

    @staticmethod
    def from_line(line, line_index):
        line = line.strip()
        start = line.find("\"")
        end = line.find("\"", start+1)

        splitted = line[end+1:].strip().split(' ')
        return ZlmLayer(line[start+1: end], float(splitted[0]), int(splitted[1]), line_index)

    def zbrush_index(self):
        if self.master:
            return len(self.master.instances_list) - self.index
        return 0

    def __repr__(self):
        return f"ZlmLayer({self.name}, {self.intensity}, {self._mode}, {self.index})"


class ZlmLayers(object):
    cb_layer_created = 0
    cb_layer_removed = 1
    cb_layer_updated = 2
    cb_layer_renamed = 3
    cb_layers_changed = 4

    def __init__(self):
        self.instances = {}
        self.instances_list: List[ZlmLayer] = []

        self.current_sub_tool: int = 0
        self.subtools: List[ZlmSubTool] = []

        self.recording_layer = None

        self._cb_on_layer_created = []
        self._cb_on_layer_removed = []
        self._cb_on_layer_updated = []
        self._cb_on_layer_renamed = []
        self._cb_on_layers_changed = []

    def add_callback(self, cb_type, callback):
        if cb_type == 0:
            self._cb_on_layer_created.append(callback)
        elif cb_type == 1:
            self._cb_on_layer_removed.append(callback)
        elif cb_type == 2:
            self._cb_on_layer_updated.append(callback)
        elif cb_type == 3:
            self._cb_on_layer_renamed.append(callback)
        elif cb_type == 4:
            self._cb_on_layers_changed.append(callback)

    def _add_layer(self, layer, index=None):
        l = self.instances.get(layer.name, [])
        l.append(layer)
        self.instances[layer.name] = l

        if index is None:
            self.instances_list.append(layer)
        else:
            self.instances_list.insert(index, layer)
            # increase index of below layers
            for i in range(index + 1, len(self.instances_list)):
                self.instances_list[i].index += 1

            for cb in self._cb_on_layers_changed:
                cb()

        layer.master = self

    def clear(self):
        self.instances.clear()
        self.instances_list.clear()
        self.subtools.clear()

    def layers_it(self, exclude_record=True, backward=False):
        layers = self.instances_list
        if backward:
            layers = reversed(layers)

        for l in layers:
            if exclude_record and l.mode == ZlmLayerMode.record:
                continue
            yield l

    def get_first_layer_by_name(self, name):
        try:
            return self.instances[name][0]
        except:
            pass
        return None

    def create_layer(self, name, mode=ZlmLayerMode.off, intensity=1.0):
        layer = ZlmLayer(name, intensity, mode, len(self.instances_list) + 1, self)
        self._add_layer(layer)
        for cb in self._cb_on_layer_created:
            cb(layer)
        return layer

    def remove_layer(self, layer):
        if self.recording_layer == layer:
            self.recording_layer = None

        self.instances[layer.name].remove(layer)

        # remove if empty
        if len(self.instances[layer.name]) == 0:
            self.instances.pop(layer.name)

        self.instances_list.remove(layer)

        for l in self.instances_list[layer.index-1:]:
            l.index -= 1

        for cb in self._cb_on_layer_removed:
            cb(layer)
        return layer

    def rename_layer(self, layer, new_name):
        if new_name and new_name != layer.name:
            self.instances[layer.name].remove(layer)
            # remove if empty
            if len(self.instances[layer.name]) == 0:
                self.instances.pop(layer.name)

            old_name = layer.name
            new_name = self.validate_layer_name(new_name)
            layer.name = new_name
            l = self.instances.get(new_name, [])
            l.append(layer)
            self.instances[new_name] = l

            for cb in self._cb_on_layer_renamed:
                cb(layer, old_name)
            return True
        return False

    def duplicate_layer(self, layer, move_down=False):
        suf = '_dup'
        new_name = layer.name
        needed_len = max_name_len - len(suf)
        if len(new_name) <= needed_len:
            new_name += suf
        else:
            new_name = new_name[:needed_len]
            if new_name[-1] == '_' == suf[0]:
                new_name += suf[1:]
            else:
                new_name += suf
        new_name = self.validate_layer_name(new_name)
        index = len(self.instances_list) if move_down else layer.index
        new_layer = ZlmLayer(new_name, 1.0, 0, index + 1, self)
        self._add_layer(new_layer, None if move_down else index)

        for cb in self._cb_on_layer_created:
            cb(new_layer)

        return layer, new_layer

    def _parse_layer(self, lines: List[str]) -> int:
        # layer index starts a 1
        for x, line in enumerate(lines, 1):
            if line.startswith('SubTools:'):
                return x - 1
            self._add_layer(ZlmLayer.from_line(line, x))
        return 0

    def _parse_subtool_line(self, lines: List[str]):
        if not lines:
            return

        line = lines[0].strip()
        # get current subtool
        self.current_sub_tool = int(line.split(' ')[1])
        for index, line in enumerate(lines[1:]):
            self.subtools.append(ZlmSubTool.from_line(line, index))

    def load_from_file(self, file_path):
        self.clear()

        with open(file_path, mode='r') as f:
            lines = f.readlines()
        try:
            layer_end = self._parse_layer(lines)
            self._parse_subtool_line(lines[layer_end:])
        except:
            pass

        for cb in self._cb_on_layer_updated:
            cb()

    def validate_layer_name(self, name):
        _, name = self.remove_invalid_char(name)
        if name not in self.instances:
            return name[:max_name_len]

        number = 1
        # replace number with new number
        match = re.search(r'(\d+)$', name)
        if match:
            name = name[:match.span()[0]]
            number = int(match.group(0)) + 1

        # make sure we dont bust 15 char lenght
        pad = max(2, len(str(number)))
        name = name[:max_name_len - pad]
        name = f'{name}{number:02d}'
        return self.validate_layer_name(name)

    def remove_name_duplicate(self):
        modified_layers = []
        dup_names = []
        for key, layers in self.instances.items():
            if len(layers) > 1:
                dup_names.append(key)

        for dup_name in dup_names:
            for layer in list(self.instances[dup_name]):
                new_name = self.validate_layer_name(layer.name)
                self.rename_layer(layer, new_name)
                modified_layers.append(layer)
        return modified_layers

    def remove_invalid_char(self, name):
        new_name = invalid_char_re.sub('', name)
        return name != new_name, new_name

    def fix_up_names(self):
        modified_layers = set()
        for layer in self.instances_list:
            mod, new_name = self.remove_invalid_char(layer.name)
            if mod and self.rename_layer(layer, new_name):
                modified_layers.add(layer)

        modified_layers.update(self.remove_name_duplicate())

        return modified_layers

    def merge_layers(self, layers):
        # start by removing biggest index because we dont want to affect the index
        sorted_layers = sorted(layers, key=lambda l: l.index, reverse=True)
        keep_layer = sorted_layers[-1]
        for l in sorted_layers[:-1]:
            self.remove_layer(l)
        return keep_layer


main_layers = ZlmLayers()


def get_preset_folders():
    """ Look for preset folder
    1. With the executable
    2. In the user
    """

    out = {
        'app': [],
        'user': None
    }

    if getattr(sys, 'frozen', False):
        root = sys.executable
    else:
        root = __file__

    directory = os.path.join(os.path.dirname(root), 'presets')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    out['app'].append(directory)

    settings = ZlmSettings.instance()
    for directory in settings.additionnal_preset_dir:
        if os.path.isdir(directory):
            out['app'].append(directory)

    try:
        for directory in os.environ['ZLM_PRESET_PATH'].split(';'):
            if os.path.isdir(directory):
                out['app'].append(directory)
    except:
        pass

    directory = os.path.join(settings.getsettingfolder(), 'presets')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    out['user'] = directory

    return out


def get_preset_file():
    folders = get_preset_folders()
    out = {}
    for key, value in folders.items():
        if value:
            try:
                if not isinstance(value, list):
                    value = [value]
                
                files = []
                for d in value:
                    files.extend(os.path.join(d, f) for f in os.listdir(d) if '.json' in f)
                out[key] = tuple(files)
            except Exception as e:
                pass
        else:
            out[key] = ()
    return out


def validate_new_preset_file(preset_name):
    if not preset_name:
        return False

    folders = get_preset_folders()
    user_folder = folders['user']
    full_path = os.path.join(user_folder, preset_name + '.json')
    return not os.path.exists(full_path)


def create_new_preset_file(preset_name):
    folders = get_preset_folders()
    user_folder = folders['user']
    full_path = os.path.join(user_folder, preset_name + '.json')

    f = open(full_path, mode='w')
    f.write('{}')
    f.close()


def remove_preset_file(preset_name):
    folders = get_preset_folders()
    user_folder = folders['user']
    full_path = os.path.join(user_folder, preset_name + '.json')

    try:
        os.remove(full_path)
    except:
        pass


def load_presets():
    preset_files = get_preset_file()
    out = {}
    for key, value in preset_files.items():
        out[key] = {}
        for f in value:
            filename = os.path.basename(f).split('.')[0]
            with open(f, mode='r') as filobj:
                # avoid any error with json.
                try:
                    out[key][filename] = json.load(filobj)
                except:
                    pass
    return out


def get_layers_as_preset():
    out = {
        'active': [],
        'record': None
    }

    for layer in main_layers.instances_list:
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

    for layer in main_layers.instances_list:
        layer.intensity = 1.0
        layer.mode = 0
    main_layers.recording_layer = None

    for layer in preset.get('active', []):

        name = layer.get('name', None)
        if name is None:
            break

        layers = main_layers.instances.get(name, None)
        if layers:
            cl = None
            if len(layers) > 1:
                index = layer.get('index', None)
                if index is not None:
                    # check for index in the array of layer with the same name
                    for l in layers:
                        if l.index == index:
                            cl = l
                            break
                    # layer not found, do nothing.
            else:
                cl = layers[0]

            if cl:
                cl.mode = 2
                cl.intensity = layer.get('intensity', 1.0)

    record = preset.get('record', None)
    if record:
        name = record.get('name', None)

        if name is not None:
            layers = main_layers.instances.get(name, None)

            if layers:
                cl = None
                if len(layers) > 1:
                    index = layer.get('index', None)
                    if index is not None:
                        # check for index in the array of layer with the same name
                        for l in layers:
                            if l.index == index:
                                cl = l
                                break
                        # layer not found, do nothing.
                else:
                    cl = layers[0]

                if cl:
                    cl.mode = 1
                    cl.intensity = 1.0

                    main_layers.recording_layer = cl


def save_layers_preset(name, data):
    folder = get_preset_folders()
    filepath = os.path.join(folder['user'], name + '.json')

    with open(filepath, mode='w') as f:
        json.dump(data, f, indent=4)


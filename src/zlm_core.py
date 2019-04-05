from collections import OrderedDict
from enum import Enum


class ZlmLayerMode(Enum):
    off = 0
    record = 1
    active = 2


class ZlmLayer(object):
    def __init__(self, name, intensity, mode, index):
        self.name = name
        self.intensity = intensity
        self.mode = mode
        self.index = index

    @staticmethod
    def from_line(line, line_index):
        line = line.strip()
        splitted = line.split(' ')
        return ZlmLayer(splitted[0], splitted[1], splitted[2], line_index)


class ZlmSubTool(object):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    @staticmethod
    def from_line(line):
        line = line.strip()
        splitted = line.split(' ')
        return ZlmSubTool(splitted[0], splitted[1])


def parse_layer_file(file_path):
    """Parse the given layers file and return the list of layer

    Args:
        file_path (str): The file path

    Returns: (layersList, subtoolName)
    """
    outDict = OrderedDict()
    subTool = None

    with open(file_path, mode='r') as f:
        lines = f.readlines()
        # last line is for subtools
        for x, line in enumerate(lines[:-1]):
            layer = ZlmLayer.from_line(line, x)
            outDict[layer.name] = layer

        subTool = ZlmSubTool.from_line(lines[-1])

    return outDict, subTool

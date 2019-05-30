import os
import sys
import subprocess

import zlm_core
import zlm_settings
import zlm_zsc as zsc


startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def _send_script():
    # use start with shell=True instead ??
    subprocess.call([zlm_settings.ZBRUSH_PATH, zlm_settings.SCRIPT_PATH],
                    startupinfo=startupinfo)


def _set_layer_state():
    for l in zlm_core.main_layers.layers_it(exclude_record=True,
                                            backward=True):
        zsc.SetLayerMode(l)

    record_layer = zlm_core.main_layers.recording_layer
    if record_layer:
        record_layer.intensity = 1.0
        zsc.SetLayerMode(record_layer)


def send_to_zbrush():
    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        zsc.SubdivStore()
        zsc.SubdivMax()

        zsc.DeactivateRecord()

        _set_layer_state()

        zsc.SubdivRestore()
    _send_script()


def send_intensity(layers=None, intensity=1.0):
    if layers is None:
        layers = zlm_core.main_layers.instances_list

    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        for l in layers:
            zsc.SetIntensity(l)

    _send_script()


def export_layers(layers=None, subdiv=0, base_mesh=False):
    if layers is None:
        layers = zlm_core.main_layers.instances_list

    settings = zlm_settings.instance()
    # check if port if valid.
    dcc_import = settings.get_current_dcc_port() is not None

    out_folder = settings.working_folder
    out_format = settings.get_current_dcc_format()

    quote = zsc.Quote.get()
    if dcc_import:
        if getattr(sys, 'frozen', False):
            imp_cmd = '[ShellExecute,[StrMerge,"call ",{1},"{0}",{1}," -i ",{1},"{{}}",{1}]]'.format(zlm_settings.ZLM_PATH, quote)
        else:
            imp_cmd = '[ShellExecute,"call {} & call {} -m zlm_sender -i {{}}"]'.format(zlm_settings.ACTIVATE_SCRIPT,
                                                                                        zlm_settings.PYTHON)

    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        zsc.Quote()
        zsc.SubdivStore()
        zsc.SubdivMax()
        zsc.DeactivateRecord()

        # Deactive any active layers
        for l in zlm_core.main_layers.layers_it(exclude_record=False,
                                                backward=True):
            zsc.SetLayerMode(l.name, l.zbrush_index(), 0, 1.0)

        zsc.SubdivSet(subdiv)

        if base_mesh:
            path = os.path.join(out_folder, zlm_core.main_layers.subtool.name +
                                out_format)
            zsc.ExportMesh(path)
            if dcc_import:
                zsc.TextCommand(imp_cmd.format(path))

        for l in layers:
            path = os.path.join(out_folder, l.name + out_format)
            zsc.ExportLayer(l, path)
            if dcc_import:
                zsc.TextCommand(imp_cmd.format(path))

        zsc.SubdivMax()

        _set_layer_state()

        zsc.SubdivRestore()
    _send_script()


def import_base(file_path, vertex_count):
    _update_mesh(file_path, vertex_count)


def import_layer(file_path, name, vertex_count):
    # find layer with this name and update it
    # if no layer with this name found, create a new one.
    create_layer = False
    layer = zlm_core.main_layers.get_first_layer_by_name(name)
    if layer is None:
        layer = zlm_core.main_layers.create_layer(name)
        create_layer = True

    _update_mesh(file_path, vertex_count, layer, create_layer)


def _update_mesh(file_path, vertex_count, layer=None, create_layer=False):
    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        if layer is not None:
            if create_layer:
                zsc.CreateLayer(layer)
                # deactivate record
                # zsc.SetLayerMode(layer)

        # Deactive any active layers
        for l in zlm_core.main_layers.layers_it(exclude_record=False,
                                                backward=True):
            zsc.SetLayerMode(l.name, l.zbrush_index(), 0, 1.0)

        # if layer is specified set this layer mode to record:
        if layer is not None:
            zsc.SetLayerMode(layer.name, layer.zbrush_index(), 1, 1.0)

        zsc.UpdateMesh(file_path, vertex_count)

        zsc.SubdivMax()

        _set_layer_state()

        zsc.SubdivRestore()
    _send_script()


def create_layer(layer):
    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        # zsc.SubdivStore()

        # zsc.SubdivMax()
        # zsc.DeactivateRecord()

        zsc.CreateLayer(layer)

    _send_script()


def send_deleted_layers(layers):
    if not isinstance(layers, (list, tuple)):
        layers = [layers]

    # sort layer by index
    layers = sorted(layers, key=lambda l: l.index)

    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        layer_count = len(zlm_core.main_layers.instances_list) + len(layers)
        for layer in layers:
            idx = layer_count - layer.index
            zsc.DeleteLayer(idx)
            layer_count -= 1

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()
    _send_script()


def send_new_layers_name(layers):
    if not isinstance(layers, (list, tuple)):
        layers = [layers]

    with zsc.ZScript(zlm_settings.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        for layer in layers:
            zsc.RenameLayer(layer)

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()
    _send_script()

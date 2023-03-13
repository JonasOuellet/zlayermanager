import os
import subprocess
from typing import List

import zlm_core
import zlm_settings
import zlm_zsc as zsc
import zlm_info


startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def _send_script():
    # use start with shell=True instead ??
    zbrush = zlm_info.get_zbrush_path()
    if zbrush is None:
        print("No Zbrush running cannot send script")
        return

    subprocess.call([zbrush, zlm_info.SCRIPT_PATH],
                    startupinfo=startupinfo)


def _set_layer_state():
    for layer in zlm_core.main_layers.layers_it(exclude_record=True,
                                                backward=True):
        zsc.SetLayerMode(layer)

    record_layer = zlm_core.main_layers.recording_layer
    if record_layer:
        record_layer.intensity = 1.0
        zsc.SetLayerMode(record_layer)


def send_to_zbrush():
    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        # always preferable to go to subdiv (i think)
        # maybe it would only be needed to go to subdiv max is we have a layer recording
        zsc.SubdivMax()

        zsc.DeactivateRecord()

        _set_layer_state()

        zsc.SubdivRestore()
    _send_script()


def send_intensity(layers=None, intensity=1.0):
    if layers is None:
        layers = zlm_core.main_layers.instances_list

    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        for layer in layers:
            zsc.SetIntensity(layer)

    _send_script()


def export_layers(layers=None, subdiv=0, base_mesh=False):
    if layers is None:
        layers = zlm_core.main_layers.instances_list

    settings = zlm_settings.instance()
    # check if port if valid.
    app_port = settings.get_current_app_port()
    app_import = app_port is not None and settings.send_after_export

    out_folder = settings.get_export_folder()
    out_format = settings.get_current_app_format()

    if app_import:
        imp_cmd = """[FileExecute,"ZSOCKET.dll","SocketSend", "import zlm;zlm.zlm_import_file('{}')"]"""

    with zsc.ZScript(zlm_info.SCRIPT_PATH):

        if app_import:
            # make sure we use to good addr
            zsc.TextCommand(f'[FileExecute,"ZSOCKET.dll","SetSocketAddr","127.0.0.1:{app_port}"]')

        zsc.Quote()
        zsc.SubdivStore()
        zsc.SubdivMax()
        zsc.DeactivateRecord()

        # Deactive any active layers
        for layer in zlm_core.main_layers.layers_it(exclude_record=False,
                                                    backward=True):
            zsc.SetLayerMode(layer.zbrush_index(), 0, 1.0)

        zsc.SubdivSet(subdiv)

        if base_mesh:
            path = os.path.join(
                out_folder,
                zlm_core.main_layers.subtool.name + out_format
            )
            zsc.ExportMesh(path)
            if app_import:
                zsc.TextCommand(imp_cmd.format(path.replace('\\', '/')))

        for layer in layers:
            path = os.path.join(out_folder, layer.name + out_format)
            zsc.ExportLayer(layer, path)
            if app_import:
                zsc.TextCommand(imp_cmd.format(path.replace('\\', '/')))

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
    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        if layer is not None:
            if create_layer:
                zsc.CreateLayer(layer)
                # deactivate record
                # zsc.SetLayerMode(layer)

        # Deactive any active layers
        for layer in zlm_core.main_layers.layers_it(exclude_record=False,
                                                    backward=True):
            zsc.SetLayerMode(layer.zbrush_index(), 0, 1.0)

        # if layer is specified set this layer mode to record:
        if layer is not None:
            zsc.SetLayerMode(layer.zbrush_index(), 1, 1.0)

        # set 1 to delete file after
        zsc.UpdateMesh(file_path, vertex_count, 1)

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        _set_layer_state()

        zsc.SubdivRestore()
    _send_script()


def create_layer(layer):
    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()
        zsc.SubdivMax()
        zsc.CreateLayer(layer)
        zsc.SubdivRestore()

    _send_script()


def send_deleted_layers(layers):
    if isinstance(layers, zlm_core.ZlmLayer):
        layers = [layers]

    # sort layer by index
    layers = sorted(layers, key=lambda l: l.index)

    with zsc.ZScript(zlm_info.SCRIPT_PATH):
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
    if isinstance(layers, zlm_core.ZlmLayer):
        layers = [layers]

    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        for layer in layers:
            zsc.RenameLayer(layer)

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()
    _send_script()


def send_duplicated_layers(layers, move_down=False):
    """Send duplicated layer to zbrush

    Args:
        layers (list): Must be a list of [ZlmLayer, ZlmLayer] first layer is the source layer
            and second layer is the duplicated one.
        move_down (bool, optional): Move the layer down to the list ?. Defaults to False.
    """
    if isinstance(layers, zlm_core.ZlmLayer):
        layers = [layers]

    # sort layer by index
    layers = sorted(layers, key=lambda l: l[0].index)

    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        initial_size = len(zlm_core.main_layers.instances_list) - len(layers)
        for src, dup in layers:
            zsc.DuplicateLayer(initial_size - src.index, dup.name, move_down)
            initial_size += 1

        for _, dup in layers:
            zsc.SetLayerMode(dup)

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()
    _send_script()


def send_merged_layers(layers):
    """send merged layers, the layer with the smalled index will be kept and its index
    will remain unchanged.

    Args:
        layers ([ZlmLayer]): list of layer that just been merged.
    """
    # sort layer by index
    layers = sorted(layers, key=lambda l: l.index)
    tl = layers[0]
    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        # minus one because there is the smallest index layer that remain.
        initial_size = len(zlm_core.main_layers.instances_list) + len(layers) - 1
        tli = initial_size - tl.index - 1
        # move all layers underneath the smalled index layer
        for layer in layers[1:]:
            index = initial_size - layer.index
            if index != tli:
                zsc.MoveLayer(index, tli)
            tli -= 1

        # merge down
        zsc.MergeDown(initial_size - tl.index, len(layers) - 1)

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()
    _send_script()


def send_update_request():
    """Update layer content from zbrush
    """
    zbrush = zlm_info.get_zbrush_path()
    if zbrush is None:
        print("No Zbrush running cannot send script")
        return

    subprocess.call([zbrush, zlm_info.UPDATE_SCRIPT_PATH],
                    startupinfo=startupinfo)


def send_new_layer_order(layers: List[zlm_core.ZlmLayer]):
    """Send the new layer order and update the mains layer list.

    Args:
        layers (List[zlm_core.ZlmLayer]): _description_
    """
    # reverse layers because it is like that in zbrush
    main_layers = list(reversed(zlm_core.main_layers.instances_list))
    new_layers = list(reversed(layers))

    need_to_send = False

    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.SubdivStore()

        zsc.SubdivMax()
        zsc.DeactivateRecord()

        for x, layer in enumerate(new_layers):
            current_index = main_layers.index(layer)
            if x != current_index:
                zsc.MoveLayer(current_index, x)

                main_layers.pop(current_index)
                main_layers.insert(x, layer)

                need_to_send = True

        if zlm_core.main_layers.recording_layer:
            zsc.SetLayerMode(zlm_core.main_layers.recording_layer)

        zsc.SubdivRestore()

    if need_to_send:
        _send_script()

        # update main layer list
        main_layers = list(reversed(main_layers))
        # update all the layers indexes
        for y, l in enumerate(main_layers):
            l.index = y + 1

        zlm_core.main_layers.instances_list[:] = main_layers[:]

        # call a ui update
        for cb in zlm_core.main_layers._cb_on_layers_changed:
            cb()


def send_new_sub_tool(index: int, port: int):
    with zsc.ZScript(zlm_info.SCRIPT_PATH):
        zsc.TextCommand(f'[SubToolSelect, {index}]')

        # include update script so we update the new layers
        zsc.TextCommand(f'<zscriptinsert, "{zlm_info.UPDATE_SCRIPT_FILE}"')
    _send_script()

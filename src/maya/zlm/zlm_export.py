import os

from maya import cmds

from zlm.zlm_settings import ZlmSettings
from zlm.zlm_utils import load_obj_plugin
from zlm import zlm_sender

zlm_sender = reload(zlm_sender)


def _export_mesh(obj, settings):
    vert_count = cmds.polyEvaluate(obj, vertex=True)
    if vert_count:
        pretty_name = obj.split('|')[-1].split(':')[-1]
        export_path = os.path.join(settings.get_import_folder(), pretty_name + '.obj')

        cmds.select(obj)

        cmds.file(export_path.replace('\\', '/'), force=True, options="groups=0;ptgroups=0;materials=0;smoothing=0;normals=0",
                  typ="OBJexport", es=True)

        return export_path, pretty_name, vert_count

    else:
        raise Exception('No vertex')


def _export(objs, base=False):
    settings = ZlmSettings()

    load_obj_plugin()

    for obj in objs:
        try:
            path, name, v_count = _export_mesh(obj, settings)

            args = ['i_layer', settings, path, name, v_count]
            if base:
                args[0] = 'i_base'
                args.pop(3)
            zlm_sender.send_command(*args)

        except Exception as e:
            print "Error when exporting mesh: {}. {}".format(obj, str(e))

    cmds.select(objs)


def export_selected():
    sel = cmds.ls(selection=True)
    _export(sel)


def export_base():
    sel = cmds.ls(selection=True)
    _export([sel[0]], base=True)

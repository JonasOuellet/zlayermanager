from maya import cmds


def load_obj_plugin():
    if not cmds.pluginInfo('objExport.mll', query=True, loaded=True):
        cmds.loadPlugin('objExport.mll')

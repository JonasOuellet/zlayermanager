from maya import cmds

from zlm.zlm_settings import ZlmSettings

_LAST_OPENED_PORT = None

_IMPORT_FILE_CALLBACKS = []
_IMPORT_ALL_CALLBACKS = []


class CBType:
    import_file = 1
    import_all = 2

    types = (1, 2)


def close_port():
    if _LAST_OPENED_PORT:
        portStr = ':{}'.format(_LAST_OPENED_PORT)

        if cmds.commandPort(portStr, q=True):
            cmds.commandPort(cl=True, name=portStr)
        else:
            print "Zlm port '{}' already closed".format(port)


def open_port():
    global _LAST_OPENED_PORT

    settings = ZlmSettings()
    portStr = ':{}'.format(settings.maya_communication_port)

    if not cmds.commandPort(portStr, q=True):
        cmds.commandPort(name=portStr, sourceType='python', noreturn=True)
        _LAST_OPENED_PORT = settings.maya_communication_port
    else:
        print "Zlm port '{}' already opened".format(portStr[1:])


def callback_add(cb_type, callback):
    if cb_type == CBType.import_file:
        _IMPORT_FILE_CALLBACKS.append(callback)
    elif cb_type == CBType.import_all:
        _IMPORT_ALL_CALLBACKS.append(callback)


def callback_rem(cb_type, callback):
    if cb_type == CBType.import_file:
        try:
            _IMPORT_FILE_CALLBACKS.remove(callback)
        except:
            pass
    elif cb_type == CBType.import_all:
        try:
            _IMPORT_ALL_CALLBACKS.remove(callback)
        except:
            pass


def callback_clr(cb_type):
    if cb_type == CBType.import_file:
        _IMPORT_FILE_CALLBACKS.clear()
    elif cb_type == CBType.import_all:
        _IMPORT_ALL_CALLBACKS.clear()


def zlm_import_file(file_path):
    for cb in _IMPORT_FILE_CALLBACKS:
        cb(file_path)


def zlm_import_all():
    settings = ZlmSettings()
    folder = settings.get_export_folder()

    for cb in _IMPORT_ALL_CALLBACKS:
        cb(folder, settings.export_format)

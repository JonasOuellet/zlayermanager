import traceback

from maya import cmds

from zlm_core import ZlmSettings

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
            print "Zlm port '{}' closed.".format(_LAST_OPENED_PORT)
        else:
            print "Zlm port '{}' already closed".format(_LAST_OPENED_PORT)


def open_port():
    global _LAST_OPENED_PORT

    settings = ZlmSettings()
    port = settings.get_app_port('Maya')
    portStr = ':{}'.format(port)

    if _LAST_OPENED_PORT != port:
        close_port()

    if not cmds.commandPort(portStr, q=True):
        cmds.commandPort(name=portStr, sourceType='python', noreturn=True)
        _LAST_OPENED_PORT = port
        print "Zlm port '{}' opened.".format(port)
    else:
        print "Zlm port '{}' already opened.".format(port)


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
        # _IMPORT_FILE_CALLBACKS.clear()  # only in python 3.x +
        del _IMPORT_FILE_CALLBACKS[:]
    elif cb_type == CBType.import_all:
        # _IMPORT_ALL_CALLBACKS.clear()  # only in python 3.x +
        del _IMPORT_ALL_CALLBACKS[:]


def zlm_import_file(file_path):
    try:
        for cb in _IMPORT_FILE_CALLBACKS:
            cb(file_path)
    except:
        print 'Zlm - Error when importing file "{}":'.format(file_path)
        traceback.print_exc()

def zlm_import_all():
    settings = ZlmSettings()
    folder = settings.get_export_folder()

    try:
        for cb in _IMPORT_ALL_CALLBACKS:
            cb(folder, settings.export_format)
    except:
        print 'Zlm - Error when importing files:'
        traceback.print_exc()    

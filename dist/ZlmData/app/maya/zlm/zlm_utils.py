from functools import wraps

from maya import cmds


def load_obj_plugin():
    if not cmds.pluginInfo('objExport.mll', query=True, loaded=True):
        cmds.loadPlugin('objExport.mll')


def doWithNoUndo(pFunc):
    """Decorators when executing a function without storing operation in undo stack

    To use it:

    >>> @doWithNoUndo
    >>> def functionWithNoUndo():
    >>>     pass

    :param flush: (bool) Default: False. if to flush undo stack before closing ?
    """
    @wraps(pFunc)
    def wrapper(*args, **kwargs):
        cmds.undoInfo(stateWithoutFlush=False)

        try:
            return pFunc(*args, **kwargs)

        finally:
            cmds.undoInfo(stateWithoutFlush=True)

    return wrapper

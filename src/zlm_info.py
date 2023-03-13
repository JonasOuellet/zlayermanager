import sys
import os
import psutil


ZBRUSH_PATH = None
LAYER_INDEX = 368
UPDATE_SCRIPT_FILE = 'zLayerUpdate.TXT'


if getattr(sys, 'frozen', False):
    # frozen
    dirname = os.path.dirname(sys.executable)
    SCRIPT_PATH = os.path.join(dirname, 'zlm.TXT')
    LAYER_PATH = os.path.join(dirname, "layers.TXT")

    UPDATE_SCRIPT_PATH = os.path.join(dirname, UPDATE_SCRIPT_FILE)

else:
    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    SCRIPT_PATH = os.path.join(dirname, 'dist', 'ZlmData', 'zlm.TXT')
    LAYER_PATH = os.path.join(dirname, 'dist', 'ZlmData', 'layers.TXT')
    UPDATE_SCRIPT_PATH = os.path.join(dirname, 'dist', 'ZlmData', UPDATE_SCRIPT_FILE)


def get_zbrush_path() -> str:
    """Since only one version of zbrush can run at the same time
    find it with the process.

    Returns:
        str: path to zbrush exec.
    """
    global ZBRUSH_PATH
    if ZBRUSH_PATH:
        return ZBRUSH_PATH

    processName = 'zbrush.exe'
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName in proc.name().lower():
                ZBRUSH_PATH = proc.exe()
                return ZBRUSH_PATH
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

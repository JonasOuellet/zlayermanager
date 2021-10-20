import subprocess
from pathlib import Path
import sys

from zlm_sender.communicate import Connection
from zlm_app import send_app_cmd


def open(file_path=None, layer_id=None,):
    conn = Connection()
    # error when connecting so it means that the UI is not opened
    if not conn.connect():
        if getattr(sys, 'frozen', False):
            args = [str(Path(sys.executable).parent.joinpath('zlm_ui.exe'))]
        else:
            python_path = Path(sys.executable)
            name, ext = python_path.name.split('.')
            args = [str(python_path.with_name(name + 'w.' + ext)),
                    str(Path(__file__).parent.parent.joinpath('zlm_ui'))
                    ]

        if layer_id is not None:
            args.append(str(layer_id))

        if file_path:
            args.extend([str(file_path)])

        # start process detached
        subprocess.Popen(args,
                         # https://stackoverflow.com/questions/54095012/start-detached-infinite-process-with-python-on-windows-and-pipe-the-output-into
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | \
                         subprocess.CREATE_BREAKAWAY_FROM_JOB
                         )

    elif file_path:
        # pass the file path to the ui so it update
        conn.send('update', file_path)

    conn.close()


def app_import(file_path):
    command = "import zlm;zlm.zlm_import_file('{}')".format(file_path.replace('\\', '/'))
    send_app_cmd(command)


def update_from_zbrush():
    conn = Connection()
    # error when connecting so it means that the UI is not opened
    if conn.connect():
        conn.send('update_from_zbrush')
    conn.close()


def update_zbrush():
    conn = Connection()
    # error when connecting so it means that the UI is not opened
    if conn.connect():
        conn.send('update_zbrush')
    conn.close()

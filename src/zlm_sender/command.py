import os
import sys

from zlm_sender.communicate import Connection
from zlm_app import send_app_cmd


def open(file_path=None):
    conn = Connection()
    # error when connecting so it means that the UI is not opened
    if not conn.connect():
        if not getattr(sys, 'frozen', False):
            command = 'start "" E:\\zLayerManager\\src\\zlm_env\\Scripts\\python36w.exe E:\\zLayerManager\\src\\zlm_ui'
            if file_path:
                if ' ' in file_path:
                    command += ' "{}"'.format(file_path)
                else:
                    command += ' {}'.format(file_path)
            os.system(command)

        else:
            executable = os.path.join(os.path.dirname(sys.executable), 'zlm_ui.exe')

            command = 'start "" '
            if ' ' in executable:
                command += '"{}"'.format(executable)
            else:
                command += executable

            if file_path:
                if ' ' in file_path:
                    command += ' "{}"'.format(file_path)
                else:
                    command += ' {}'.format(file_path)

            os.system(command)

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
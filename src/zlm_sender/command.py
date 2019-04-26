import os
import sys
import socket

from zlm_sender.communicate import Connection, ZlmSettings


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


def maya_import(file_path):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', ZlmSettings.instance().maya_communication_port))

        command = "import zlm;zlm.zlm_import_file('{}')".format(file_path.replace('\\', '/'))
        command = bytes(command, 'utf-8')
        client.send(command)
    except:
        raise
    finally:
        client.close()

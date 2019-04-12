import os
import sys

from zlm_sender.communicate import Connection


def open(file_path=None):
    conn = Connection()
    # error when connecting so it means that the UI is not opened
    if not conn.connect():
        if not getattr(sys, 'frozen', False):
            command = 'start E:\\zLayerManager\\src\\zlm_env\\Scripts\\python36w.exe E:\\zLayerManager\\src\\zlm_ui'
            if file_path:
                if ' ' in file_path:
                    command += ' "{}"'.format(file_path)
                else:
                    command += ' {}'.format(file_path)
            os.system(command)

        else:
            pass

    elif file_path:
        # pass the file path to the ui so it update
        conn.send('update', file_path)

    conn.close()

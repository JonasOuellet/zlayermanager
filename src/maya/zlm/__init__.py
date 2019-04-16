""" To use it in maya:
1. copy the folder to maya folder script
2. edit usersetup.py:```
>>> import zlm
>>> # open communication port
>>> zlm.open_port()
>>> # add default callback when import is requested
>>> # you can specify any callback (function) that take 1 argument (the file path to import)
>>> zlm.callback_add(zlm.CBType.import_file, zlm.import_file)
>>> # add default callback when import all is requested
>>> # import all callback must take two args (folder_path, extension)
>>> zlm.callback_add(zlm.CBType.import_all, zlm.import_files)
>>> # remove all files in folder after import
>>> zlm.callback_add(zlm.CBType.import_all, zlm.clean_folder)
"""

from zlm.zlm_core import CBType, open_port, close_port, callback_add, callback_rem, callback_clr, zlm_import_file, zlm_import_all
from zlm.zlm_import import import_file, remove_file, import_files, clean_folder

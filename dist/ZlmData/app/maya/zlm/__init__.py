""" To use it in maya:
Location your installation of ZLayerManager in the zbrush startup folder
it should be something like that:
C:\Program Files\Pixologic\ZBrush 2018
```
>>> # add zlm script folder to sys path
>>> import sys
>>> sys.path.append(r"{path to zbrush}\ZStartup\ZPlugs64\ZlmData\app\maya)
>>> import zlm
>>> # open communication port so maya can receive command
>>> zlm.open_port()
```
"""

# make sure to have access to zlm_core which is in the app folder
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                os.pardir, os.pardir)))

from zlm.core import CBType, open_port, close_port, callback_add, callback_rem, callback_clr, zlm_import_file, zlm_import_all
from zlm.zlm_import import import_file, remove_file, import_files, clean_folder
from zlm.zlm_export import export_base, export_selected

# add default callback when import is requested
# you can specify any callback (function) that take 1 argument (the file path to import)
callback_add(CBType.import_file, import_file)
# add default callback when import all is requested
# import all callback must take two args (folder_path, extension)
callback_add(CBType.import_all, import_files)
# remove all files in folder after import
callback_add(CBType.import_all, clean_folder)

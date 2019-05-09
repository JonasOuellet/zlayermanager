# zLayerManager

## Description

Help working with layers in zBrush with a custom user interface. 

## Maya

Setuping maya to be able to import blendshape directly:

1. Copy zlm maya python package to a maya script folder
2. Edit `userSetup.py` file to start zlm communication port and import callback function.
```python
import zlm
# open communication port
zlm.open_port()

# add default callback when import is requested
# you can specify any callback (function) that take 1 argument (the file path to import)
zlm.callback_add(zlm.CBType.import_file, zlm.import_file)

# add default callback when import all is requested
# import all callback must take two args (folder_path, extension)
zlm.callback_add(zlm.CBType.import_all, zlm.import_files)
# remove all files in folder after import
zlm.callback_add(zlm.CBType.import_all, zlm.clean_folder)
```

**Notes:** You can specify any import callback, in this exemple, default import callback are used.  When importing a blendshape, it check if there is a mesh with the same name in the scene, if soo, it will update it vertex position with the new mesh and delete the new mesh.  Oterwise, it will keep the new imported mesh in the scene.


## Set up development environment

### Installing python

You well need a python 3.6 installation to execute the scripts.

### Creating python virtual environment

Open a console in the `.\src` directory then enter the following:

```bash
> python36 -m venv zlm_env
> python36 -m pip install -r requirements.txt
```

**Notes:** You might need to use `python` if you onyl have one version of python installed.

#### Edit activation script to add the src folder to the python path

Add this `set PYTHONPATH=E:\zLayerManager\src;%PYTHONPATH%` to the bottom off the activate script. Replace the path depending off your location to the src folder.

Activate script is located here `zlm_env\Scripts\activate.bat` on windows or here `zlm_env/bin/activate` for linux or macosx.



#### To Activate the virtual environment

On windows:

```bash
> zlm_env\Scripts\activate.bat
```

On Linux:
```bash
> source zlm_env/bin/activate
```

#### To Deactivate the virtual environment

Enter `deactivate` in the console.



## Build

To build you have to navigate to `src` folder

#### Building zlm.exe
```bash
pyinstaller --distpath ..\dist\ZlmData zlm.spec
```

#### Building zlm_ui.exe
```bash
pyinstaller --distpath ..\dist\ZlmData zlm_ui.spec
```




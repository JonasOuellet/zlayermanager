# zLayerManager

## Description

Help working with layers in zBrush with a custom user interface. 

## Maya

Setuping maya to be able to import blendshape directly:

```python
>>> # add zlm script folder to sys path
>>> import sys
>>> sys.path.append(r"{path to dist}\ZlmData\app\maya")
>>> import zlm
>>> # open communication port so maya can receive command
>>> zlm.open_port()
```

**Notes:** You can specify any import callback, in this exemple, default import callback are used.  When importing a blendshape, it check if there is a mesh with the same name in the scene, if soo, it will update it vertex position with the new mesh and delete the new mesh.  Oterwise, it will keep the new imported mesh in the scene.


## Set up development environment

### Installing python

You well need a python 3.6 installation to execute the scripts.

### Creating python virtual environment

Open a console in the `.\src` directory then enter the following:

```bash
> python36 -m venv zlm_env
> zlm_env\Scripts\activate.bat
> python36 -m pip install -r requirements.txt
```

**Notes:** You might need to use `python` if you only have one version of python installed.

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

If you are on windows 10 make sure you have windows devkit 10 installed.

If not you can download it [here.](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)

You might also need to change `pathex` value in zlm.spc and zlm_ui.spec to match your location of windows sdk library.


To build you have to navigate to `src` folder and activate the virtual environment.

#### Building zlm.exe
```bash
pyinstaller --distpath ..\dist\ZlmData zlm.spec
```

#### Building zlm_ui.exe
```bash
pyinstaller --distpath ..\dist\ZlmData zlm_ui.spec
```




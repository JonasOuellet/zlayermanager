# zLayerManager

## Description

Help working with layers in zBrush with a custom user interface. 

## How to Contribute 

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



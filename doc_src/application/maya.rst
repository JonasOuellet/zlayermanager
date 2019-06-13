Maya
====

To setup `Maya` so ZLayerManager can export and import meshes from it, you have to edit the `userSetup.py` file
located in a `scripts` folder under Maya application directory. 

This is usually located here: **C:\\Users\\{username}\\Documents\\maya\\scripts**.

If you can't find this folder you can execute this **mel** code in Maya to retrieve it.

.. code-block:: bash

    getenv "MAYA_APP_DIR"

Locate `ZStartup\\ZPlugs64\\ZlmData\\app\\maya` folder under Zbrush installation folder.  Copy the path, replace it in the code bellow then
add it to the `userSetup.py` file. *(The file might not exists so you'll need to create one)*

.. code-block:: python
    
    # put you path between the quotes. ex: zlm_maya_app = r"YOUR PATH HERE"
    zlm_maya_app = r"C:\Program Files\Pixologic\ZBrush 2018\ZStartup\ZPlugs64\ZlmData\app\maya"

    # add zlm maya script folder to sys path
    import sys
    sys.path.append(zlm_maya_app)
    import zlm
    # open communication port so maya can receive command
    zlm.open_port()

Restart maya.

You are now setup to use `Maya` with Zbrush and Zlm.

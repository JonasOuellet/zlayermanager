Installation
============

Zlm is only available for windows for now. However, if you are a more advance user you can build it from
source, see how on the project `github
<https://github.com/JonasOuellet/zLayerManager>`_. 


Download
--------

You can download the latest version `here
<https://www37.zippyshare.com/d/jEVxvUFP/50254/ZLayerManager.zip>`_.


Install
-------

Once the `ZLayerManager.zip` is downloaded:

1. Navigate to your Zbrush plugin folder (it should be something like *C:\\Program Files\\Pixologic\\ZBrush 2018\\ZStartup\\ZPlugs64*).

2. **If you have already installed a version of ZLayerManager before**, make sure to follow these steps, otherwise you can go 
to step 3.

    #. Close Zbrush
    #. Search for these files and delete them

        * ZlmData
        * zLayerManager.txt
        * zLayerManager.zsc

3. Extract the content of `ZLayerManager.zip` in the current `ZPlugs64` folder. (You should now see a new file `zLayerManager.txt` and a new folder `ZlmData`).
4. Open Zbrush
5. Open the `Zscript` palette and click on `Load`
6. Browse to the previously extracted `zLayerManager.txt` file.
7. You should now see the `zLayerManager` menu at the bottom of the `Zplugin` palette.
8. ZLayerManager is now ready to use !

Click on `open` to open the standalone UI.

.. raw:: html

    <div style="padding: 15px; margin-left:40px; margin-bottom: 30px; background-color: rgb(255, 253, 209);
    border: 5px groove black; border-radius: 10px;">
    <h3>Warning</h3>You must have a subtool selected to open the UI
    </div>



Application
------------

ZLayerManager can be use as a bridge between ZBrush and other application.  It facilitate the process of exporting and importing mesh
from your favorite 3D software.  

It can be used to quickly update blendshape and see the result in action.

Right now, Zlm only support Maya, but it is possible to develop your own package for the application of your choice.


.. toctree::

   application/maya

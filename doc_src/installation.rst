Installation
============

Zlm is **only available for windows** for now. However, if you are a more advance user you can build it from
source, see how on the project `github
<https://github.com/JonasOuellet/zLayerManager>`_. 

.. raw:: html

    <!-- https://jameshfisher.com/2017/08/30/how-do-i-make-a-full-width-iframe/ -->
    <div style="position:relative;padding-top:56.25%;margin-bottom:60px">
        <iframe src="https://player.vimeo.com/video/665455824" frameborder="0" allowfullscreen
            style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe>
    </div>


Download
--------

You can download the latest version `here
<https://github.com/JonasOuellet/zlayermanager/releases>`_.


Install
-------

Once the `ZLayerManager.zip` is downloaded:

1. Navigate to your Zbrush plugin folder (it should be something like *C:\\Program Files\\Pixologic\\ZBrush 2018\\ZStartup\\ZPlugs64*).

2. **If you have already installed a version of ZLayerManager before**, make sure to follow these steps, otherwise you can go 
to step 3.

    #. Close Zbrush and Zlm
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

.. warning::
    - If this is the first time you use the tool and it freeze ZBrush when opening it, the os is preventing you from using the tool, you have to open it manually and say that you trust the tool.
      
      - Close Zbrush
      - Navigate to `ZlmData/zlm_ui.exe` and open it.
      - Awnser trust and open anyway.

    - You must have a subtool selected to open the UI



Application
------------

ZLayerManager can be use as a bridge between ZBrush and other application.  It facilitate the process of exporting and importing mesh
from your favorite 3D software.  

It can be used to quickly update blendshape and see the result in action.

Right now, Zlm only support Maya, but it is possible to develop your own package for the application of your choice.


.. toctree::

   application/maya

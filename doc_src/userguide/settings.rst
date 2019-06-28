Settings
========

This is the UI where the user will edit all the settings for the tool.  The edited settings are not saved until the users
**Accept** the change.

.. image:: ../_static/zlm_settings.png
   :class: align-right
   :scale: 65 %

Core
----

**File Folder:** Where files will be exported.

**Window always on top:** Set Zlm window to be on top of other windows.

**Check for update:** Check for any updates when the tool launch.


External Application
--------------------

These settings must be configured to be able to use ZLm has a bridge between Zbrush and other 3D softwares.

**Send to app:** Will automaticale import the layer exported from ZBrush in the *Current Application*

**Current Application:** Select the current application to communicate with.

**Application list:** Application Name, communication port (same port has used in application
to receive command), preferred file format for export/import.

* **+** Add setting for a new application.
* **-** Remove selected application setting.
* **↻** Reset to default value.

Layer edit
----------

**Move duplicated layer down:** Will move the new layer down the layer list when the user duplicate a layer.

.. raw:: html

    <div style="padding: 15px; margin-left:40px; margin-bottom: 30px; background-color: rgb(255, 253, 209);
    border: 5px groove black; border-radius: 10px;">
    <h3>Warning</h3>This operation may drastically increase the duplication time based on the layer count and
    the position of the layer in the list
    </div>


**Ask before delete:** The user will be prompt if he really want to delete the layer(s).  Otherwise, delete the layer(s)
without asking.
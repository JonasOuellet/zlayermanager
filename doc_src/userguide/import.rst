Import
======

This is used to import blendshape from an external application in Zbrush as a layer.

When you have blendshapes in a 3D software and you want to import the shapes as a layer in Zbrush this is the way to go.  It will work fine
if you still have the target shapes, otherwise you will need to extract them.


**Note:** Layer can be exported with higher subdiv level than 1. It can also be imported back in Zbrush with a different level of subdiv.
Zlm will try to find the corresponding subdiv level to be able to import the shape properly.


**Selected as layer(s):** Import shape(s) selected in the external application into Zbrush.  It will create a new layer if the
shape name doesn't match any layer name, otherwise it will update the matching layer.

**Selected as base mesh:** Update the zbrush base mesh(current subtool) with the selected mesh in the external application.

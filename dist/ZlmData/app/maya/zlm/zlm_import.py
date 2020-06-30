import os
import glob

from maya import cmds
from maya.api import OpenMaya as om

from zlm.zlm_utils import load_obj_plugin


def import_obj(file_path):
    dirname, filename = os.path.split(file_path)
    filename, ext = os.path.splitext(filename)

    load_obj_plugin()

    # usually when import and obj mesh the imported object name will be polySurface1
    # check if there is already a polysSurface object in the scene root
    if cmds.objExists('|polySurface1'):
        import_name = '|{}_polySurface1'.format(filename)
    else:
        import_name = '|polySurface1'

    # delete the mtl file before importing, we don't really want to create a new material
    mtl_file = os.path.join(dirname, filename + '.mtl')
    if os.path.exists(mtl_file):
        os.remove(mtl_file)

    cmds.file(file_path, i=True, typ='OBJ', options='mo=0')

    # check if there is already an object with the filename in the scene
    # if so update this mesh vertex position otherwise only rename the imported mesh
    if cmds.objExists(filename):
        sel = om.MSelectionList()
        sel.add(import_name)
        sel.add(filename)

        mmesh_source = om.MFnMesh(sel.getDagPath(0))
        mmesh_target = om.MFnMesh(sel.getDagPath(1))

        if mmesh_source.numVertices != mmesh_target.numVertices:
            raise Exception("Error, imported mesh doesn't have the same vertex count. {} -> {}".format(
                mmesh_source.numVertices, mmesh_target.numVertices
            ))

        points = mmesh_source.getPoints()
        mmesh_target.setPoints(points)

        cmds.delete(import_name)
    else:
        # clean object set
        shapes = cmds.listRelatives(import_name, shapes=True, fullPath=True)
        if shapes:
            for shape in shapes:
                objGroup = cmds.listConnections(shape, type='objectSet', exactType=True, destination=False)
                if objGroup:
                    cmds.delete(objGroup)

        # polySoftEdge -a 180 -ch 1 polySurface1
        cmds.polySoftEdge(import_name, a=180, ch=1)
        cmds.delete(import_name, constructionHistory=True)

        cmds.rename(import_name, filename)

    # remove file
    os.remove(file_path)


def import_file(file_path):
    dirname, filename = os.path.split(file_path)
    filename, ext = os.path.splitext(filename)

    cmds.undoInfo(stateWithoutFlush=False)
    sel = cmds.ls(selection=True)

    print 'zlm - Importing "{}"...'.format(filename)
    try:
        if ext.lower() == '.obj':
            import_obj(file_path)

        print 'zlm - Import Successfull.'
    finally:
        cmds.select(sel)
        cmds.undoInfo(stateWithoutFlush=True)


def remove_file(file_path):
    dirname, filename = os.path.split(file_path)
    filename, ext = os.path.splitext(filename)

    pattern = os.path.join(dirname, filename + '.*')

    files = glob.glob(pattern)

    for f in files:
        os.remove(f)


def import_files(folder, ext):
    ext_lower = ext.lower()
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(ext_lower)]

    progress = cmds.progressWindow(title='ZlmImport', maxValue=len(files), status=' ' * 15)

    for filepath in files:
        dirname, filename = os.path.split(filepath)
        filename, ext = os.path.splitext(filename)

        cmds.progressWindow(progress, e=True, status=filename)
        import_file(filepath)
        cmds.progressWindow(progress, e=True, step=1)

    clean_folder(folder, ext)
    cmds.progressWindow(progress, e=True, endProgress=True)


def clean_folder(folder, ext):
    for f in os.listdir(folder):
        fullpath = os.path.join(folder, f)
        try:
            os.remove(fullpath)
        except:
            pass

import os
from pathlib import Path
import subprocess
import shutil


WIN_DLL_PATH = r'C:\Program Files (x86)\Windows Kits\10\Redist\10.0.18362.0\ucrt\DLLs\x64'


if __name__ == '__main__':
    root = Path('.').resolve()

    src = root.joinpath('src').resolve()
    os.chdir(src)

    # add dll to path
    print("add dll to path")
    os.environ['PATH'] = os.environ['PATH'] + ';' + WIN_DLL_PATH

    builddir = root.joinpath("build")
    if builddir.exists():
        print(f"delete current build dir {builddir}")
        shutil.rmtree(builddir)

    print("Building zlm.spec")
    subprocess.check_call(['pyinstaller', '--distpath', str(builddir), 'zlm.spec'])

    print("Building zlm_ui.spec")
    subprocess.check_call(['pyinstaller', '--distpath', str(builddir), 'zlm_ui.spec'])

    zlmdata = root.joinpath("dist", "ZlmData")
    cmd = ['robocopy', str(builddir.joinpath('zlm_ui')), str(zlmdata), '/e', '/is', '/it']
    ret = subprocess.call(cmd, shell=True)
    if ret >= 8:
        raise(Exception("robocopy error"))

    print("Copying zlm.exe into dist/ZlmData")
    shutil.copy2(builddir.joinpath('zlm', 'zlm.exe'), zlmdata.joinpath('zlm.exe'))

    to_remove = [
        '..\\zLayerManager.zsc'
        "zLayerUpdate.zsc",
        "zlm.zsc",
        "zlm.txt",
        "zlmOps.zsc",
        "layers.txt",

        "d3dcompiler_47.dll",
        "opengl32sw.dll",
        "libGLESv2.dll",
        "libEGL.dll",
        "Qt5QuickShapes.dll",
        "Qt5QuickTemplates2.dll",
        "Qt5QuickTest.dll",
        "Qt5QuickWidgets.dll",
        "Qt5Xml.dll",
        "Qt5XmlPatterns.dll",
        "Qt53DRender.dll",
        "Qt5Qml.dll",
        "Qt5Quick.dll",
        "Qt5QuickControls2.dll",
        "Qt5QuickParticles.dll",
        "Qt5OpenGL.dll",
        "Qt53DQuickScene2D.dll",
        "Qt53DAnimation.dll",
        "Qt53DCore.dll",
        "Qt53DInput.dll",
        "Qt53DLogic.dll",

        "Qt5Designer.dll",
        "Qt5Location.dll",
        "Qt5Network.dll",
        "Qt5NetworkAuth.dll",

        "Qt5MultimediaQuick.dll",
        "Qt5MultimediaWidgets.dll",
        "Qt5Multimedia.dll",

        "Qt5Sql.dll",
        "Qt5Test.dll",
        "Qt5WebChannel.dll",
        "Qt5WebSockets.dll",
        "Qt5Positioning.dll",
        "Qt5PositioningQuick.dll",
        "Qt5PrintSupport.dll",
        "Qt5RemoteObjects.dll",
        "Qt5Sensors.dll",

        r"PyQt5\QtOpenGL.pyd",
        r"PyQt5\QtQml.pyd",
        r"PyQt5\QtQuick.pyd",
        r"PyQt5\QtQuickWidgets.pyd",
        r"PyQt5\QtXml.pyd",
        r"PyQt5\QtXmlPatterns.pyd",

        r"PyQt5\Qt\plugins\imageformats\qwbmp.dll",
        r"PyQt5\Qt\plugins\imageformats\qwebp.dll",
        r"PyQt5\Qt\plugins\imageformats\qtga.dll",
        r"PyQt5\Qt\plugins\imageformats\qtiff.dll",
    ]

    for f in to_remove:
        fullpath = zlmdata.joinpath(f).resolve()
        if fullpath.exists():
            print(f"Delete {fullpath}")
            os.remove(fullpath)

    folder_to_remove = [r"PyQt5\Qt\qml", r"PyQt5\Qt\translations"]
    for f in folder_to_remove:
        fullpath = zlmdata.joinpath(f).resolve()
        if fullpath.exists():
            print(f"Delete {fullpath}")
            shutil.rmtree(fullpath)

    for f in zlmdata.joinpath("app").glob("**\\*.pyc"):
        print(f"Delete {f}")
        os.remove(f)

    print("copying zlm_settings to Dist/ZlmData/app/zlm_core")
    shutil.copy2(src.joinpath("zlm_settings.py"), zlmdata.joinpath('app', 'zlm_core', 'zlm_settings.py'))

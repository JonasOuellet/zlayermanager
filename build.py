import os
from pathlib import Path
import subprocess
import shutil



if __name__ == '__main__':
    print("Building zlm.spec")
    subprocess.check_call(['pyinstaller', '-y', '--distpath', "dist", 'src/zlm.spec'])

    print("Building zlm_ui.spec")
    subprocess.check_call(['pyinstaller', '-y', '--distpath', "dist", 'src/zlm_ui.spec'])

    cmd = ['robocopy', "dist/zlm_ui", "dist/ZlmData", '/e', '/is', '/it']
    ret = subprocess.call(cmd, shell=True)
    if ret >= 8:
        raise Exception("robocopy error")

    print("Copying zlm.exe into dist/ZlmData")
    shutil.copy2("dist/zlm/zlm.exe", "dist/ZlmData/zlm.exe")

    to_remove = [
        '..\\zLayerManager.zsc'
        "zLayerUpdate.zsc",
        "zlm.zsc",
        "zlm.txt",
        "zlmOps.zsc",
        "layers.txt",

        "_internal/PyQt5/Qt5/bin/d3dcompiler_47.dll",
        "_internal/PyQt5/Qt5/bin/opengl32sw.dll",
        "_internal/PyQt5/Qt5/bin/libGLESv2.dll",
        "_internal/PyQt5/Qt5/bin/libEGL.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickShapes.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickTemplates2.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickTest.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickWidgets.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Xml.dll",
        "_internal/PyQt5/Qt5/bin/Qt5XmlPatterns.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DRender.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Qml.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Quick.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickControls2.dll",
        "_internal/PyQt5/Qt5/bin/Qt5QuickParticles.dll",
        "_internal/PyQt5/Qt5/bin/Qt5OpenGL.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DQuickScene2D.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DAnimation.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DCore.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DInput.dll",
        "_internal/PyQt5/Qt5/bin/Qt53DLogic.dll",

        "_internal/PyQt5/Qt5/bin/Qt5Designer.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Location.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Network.dll",
        "_internal/PyQt5/Qt5/bin/Qt5NetworkAuth.dll",

        "_internal/PyQt5/Qt5/bin/Qt5MultimediaQuick.dll",
        "_internal/PyQt5/Qt5/bin/Qt5MultimediaWidgets.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Multimedia.dll",

        "_internal/PyQt5/Qt5/bin/Qt5Sql.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Test.dll",
        "_internal/PyQt5/Qt5/bin/Qt5WebChannel.dll",
        "_internal/PyQt5/Qt5/bin/Qt5WebSockets.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Positioning.dll",
        "_internal/PyQt5/Qt5/bin/Qt5PositioningQuick.dll",
        "_internal/PyQt5/Qt5/bin/Qt5PrintSupport.dll",
        "_internal/PyQt5/Qt5/bin/Qt5RemoteObjects.dll",
        "_internal/PyQt5/Qt5/bin/Qt5Sensors.dll",

        r"_internal\PyQt5\QtOpenGL.pyd",
        r"_internal\PyQt5\QtQml.pyd",
        r"_internal\PyQt5\QtQuick.pyd",
        r"_internal\PyQt5\QtQuickWidgets.pyd",
        r"_internal\PyQt5\QtXml.pyd",
        r"_internal\PyQt5\QtXmlPatterns.pyd",
        r"_internal\PyQt5\QtBluetooth.pyd",
        r"_internal\PyQt5\QtBus.pyd",
        r"_internal\PyQt5\QtQml.pyd",
        r"_internal\PyQt5\QtQuick.pyd",
        r"_internal\PyQt5\QtOpenGl.pyd",
        r"_internal\PyQt5\QtSql.pyd",
        r"_internal\PyQt5\QtSvg.pyd",
        r"_internal\PyQt5\QtTest.pyd",
        r"_internal\PyQt5\QtTextToSpeech.pyd",
        r"_internal\PyQt5\QtWebChannel.pyd",
        r"_internal\PyQt5\QtWebSockets.pyd",
        r"_internal\PyQt5\QtRemoteObejcts.pyd",
        r"_internal\PyQt5\QtSensors.pyd",
        r"_internal\PyQt5\QtSerialPort.pyd",
        r"_internal\PyQt5\QtPrintSupport.pyd",
        r"_internal\PyQt5\QtMultimedia.pyd",
        r"_internal\PyQt5\QtMultimediaWidgets.pyd",
        r"_internal\PyQt5\QtNetwork.pyd",
        r"_internal\PyQt5\QtHelp.pyd",
        r"_internal\PyQt5\QtLocation.pyd",
        r"_internal\PyQt5\QtNfc.pyd",
        r"_internal\PyQt5\QtPositioning.pyd",
        r"_internal\PyQt5\QtQuick3D.pyd",
        r"_internal\PyQt5\QtRemoteObjects.pyd",
        r"_internal\PyQt5\QtDesiner.pyd",
        r"_internal\PyQt5\QtDBus.pyd",
    ]

    zlmdata = Path("dist", "ZlmData").resolve()

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
    shutil.copy2("src/zlm_settings.py", zlmdata.joinpath('app', 'zlm_core', 'zlm_settings.py'))

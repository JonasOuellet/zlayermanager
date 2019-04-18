set pysideRCC=..\zlm_env\Lib\site-packages\PySide2\pyside2-rcc.exe

set outputName=resources_rc.py
set qrcFile=resources.qrc

call %pysideRCC% -o %outputName% %qrcFile%
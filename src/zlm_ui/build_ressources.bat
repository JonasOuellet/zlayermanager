set pysideRCC=..\..\venv\Scripts\pyrcc5.exe

set outputName=resources_rc.py
set qrcFile=resources.qrc

call %pysideRCC% -o %outputName% %qrcFile%
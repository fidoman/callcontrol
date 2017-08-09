rem %~dp0python-3.6.2-amd64.exe /passive InstallAllUsers=1 CompileAll=1 PrependPath=1

powershell -Command "Start-Process pip 'install asterisk-ami' -Verb RunAs"


rem cmd /c python %~dp0microsipconf.py

rem %~dp0MicroSIP-3.15.7.exe /S

@echo off

if .%1 == .elevated goto elevated
if .%1 == .py_ok goto py_ok

set ME=%~dp0ccinstall.cmd
echo restart %ME%...
powershell -Command "Start-Process %ME% elevated -Verb RunAs"
exit 0

:elevated
echo elevated

python -V
if not errorlevel 1 goto py_ok
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.python.org/ftp/python/3.6.2/python-3.6.2.exe\", \"%~dp0python-3.6.2.exe\")"
%~dp0python-3.6.2.exe /passive InstallAllUsers=1 PrependPath=1
rem  CompileAll=1

set ME=%~dp0ccinstall.cmd
echo restart %ME%...
powershell -Command "Start-Process %ME% py_ok -UseNewEnvironment"
exit 0

:py_ok

echo installing python modules
pip install asterisk-ami

echo run configurator
python %~dp0microsipconf.py

echo install MicroSIP
rem %~dp0MicroSIP-3.15.7.exe /S


echo install git

echo install callcontrol

pause

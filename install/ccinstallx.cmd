@echo off

if .%1 == .elevated goto elevated
if .%1 == .py_ok goto py_ok
if .%1 == .bypass_git goto bypass_git

set ME=%~dp0ccinstall.cmd
echo restart %ME%...
powershell -Command "Start-Process %ME% elevated -Verb RunAs"
if errorlevel 1 goto fail
exit 0

:elevated
echo elevated

python -V
if not errorlevel 1 goto py_ok
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.python.org/ftp/python/3.6.2/python-3.6.2.exe\", \"%~dp0python-3.6.2.exe\")"
%~dp0python-3.6.2.exe /passive InstallAllUsers=1 PrependPath=1
if errorlevel 1 goto fail
rem  CompileAll=1

set ME=%~dp0ccinstall.cmd
echo restart %ME%...
powershell -Command "Start-Process %ME% py_ok -UseNewEnvironment"
if errorlevel 1 goto fail
exit 0

:py_ok

echo installing python modules
pip install asterisk-ami
if errorlevel 1 goto fail

echo run configurator
python %~dp0microsipconf.py
if errorlevel 1 goto fail

if exist %~dp0MicroSIP-3.15.7.exe goto bypass_microsip
echo install MicroSIP
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.microsip.org/downloads/?file=MicroSIP-3.15.7.exe\", \"%~dp0MicroSIP-3.15.7.exe\")"
%~dp0MicroSIP-3.15.7.exe /S
if errorlevel 1 goto fail
:bypass_microsip

if exist %~dp0Git-2.14.0.2-32-bit.exe goto bypass_git
echo install git
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://github.com/git-for-windows/git/releases/download/v2.14.0.windows.2/Git-2.14.0.2-32-bit.exe\", \"%~dp0Git-2.14.0.2-32-bit.exe\")"
%~dp0Git-2.14.0.2-32-bit.exe /silent
if errorlevel 1 goto fail
set ME=%~dp0ccinstall.cmd
echo restart %ME%...
powershell -Command "Start-Process %ME% bypass_git -UseNewEnvironment"
if errorlevel 1 goto fail
exit 0

:bypass_git

echo install callcontrol
c:
cd \
if exist callcontrol goto cc_pull
git clone https://github.com/fidoman/callcontrol
if errorlevel 1 goto fail
goto finish

:cc_pull
cd callcontrol
git pull
if errorlevel 1 goto fail

:finish
pause
exit 0

:fail
echo Error, run again
pause
exit 1

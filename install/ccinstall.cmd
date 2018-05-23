@echo off

if .%1 == .elevated goto elevated

set ME=%0
echo restart %ME%...
powershell -Command "Start-Process ""%ME%"" elevated -Verb RunAs"
exit 0

:elevated
echo elevated


set MUSTQUIT=0
rem set to 1 if installed python or git and must refresh PATH


python -V
if not errorlevel 1 goto python_ok

if exist "%~dp0python-3.6.2.exe" goto python_downloaded
echo download python
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://sergey.fidoman.ru/fastery/python-3.6.2.exe\", \"%~dp0python-3.6.2.exe\")"
:python_downloaded
echo install python

set MUSTQUIT=1
"%~dp0python-3.6.2.exe" /passive InstallAllUsers=1 PrependPath=1 CompileAll=1

:python_ok


if exist "%~dp0MicroSIP-3.16.4.exe" goto microsip_downloaded
echo download microsip
rem powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.microsip.org/downloads/?file=MicroSIP-3.15.7.exe\", \"%~dp0MicroSIP-3.15.7.exe\")"
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://sergey.fidoman.ru/fastery/MicroSIP-3.16.4.exe\", \"%~dp0MicroSIP-3.16.4.exe\")"
:microsip_downloaded
rem echo install MicroSIP
rem "%~dp0MicroSIP-3.15.7.exe" /S


git --version
if not errorlevel 1 goto git_ok

if exist "%~dp0Git-2.17.0-32-bit.exe" goto git_downloaded
echo download git
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://sergey.fidoman.ru/fastery/Git-2.17.0-32-bit.exe\", \"%~dp0Git-2.17.0-32-bit.exe\")"
:git_downloaded
echo install git
set MUSTQUIT=1
"%~dp0Git-2.17.0-32-bit.exe" /silent

:git_ok

if not %MUSTQUIT% == 1 goto part1ok

echo Prerequisites have been installed, please run again
pause 
exit

:part1ok
echo Part 1 OK

echo installing python modules
pip install asterisk-ami persist-queue selenium
if errorlevel 1 goto fail

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
rem echo run configurator
rem python c:\callcontrol\install\microsipconf.py
rem if errorlevel 1 goto fail

echo install MicroSIP
"%~dp0MicroSIP-3.16.4.exe" /S
if errorlevel 1 goto fail

echo create shortcuts
c:\callcontrol\install\shortcuts.vbs

echo Part 2 OK
pause
exit 0

:fail
echo Error, run again
pause
exit 1

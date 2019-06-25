@echo off

if .%1 == .elevated goto elevated

set ME=%0
echo restart %ME%...
powershell -Command "Start-Process \"%ME%\" elevated -Verb RunAs"
exit 0

:elevated
echo elevated


set MUSTQUIT=0
rem set to 1 if installed python or git and must refresh PATH


python -V
if not errorlevel 1 goto python_ok

if exist "%~dp0python-3.6.2.exe" goto python_downloaded
echo download python
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://www.fidoman.ru/fastery/python-3.6.2.exe\", \"%~dp0python-3.6.2.exe\")"
:python_downloaded
echo install python

set MUSTQUIT=1
"%~dp0python-3.6.2.exe" /passive InstallAllUsers=1 PrependPath=1 CompileAll=1

:python_ok


if exist "%~dp0MicroSIP-3.16.4.exe" goto microsip_downloaded
echo download microsip
rem powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.microsip.org/downloads/?file=MicroSIP-3.15.7.exe\", \"%~dp0MicroSIP-3.15.7.exe\")"
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://www.fidoman.ru/fastery/MicroSIP-3.16.4.exe\", \"%~dp0MicroSIP-3.16.4.exe\")"
:microsip_downloaded
rem echo install MicroSIP
rem "%~dp0MicroSIP-3.15.7.exe" /S


git --version
if not errorlevel 1 goto git_ok

if exist "%~dp0Git-2.17.0-32-bit.exe" goto git_downloaded
echo download git
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"http://www.fidoman.ru/fastery/Git-2.17.0-32-bit.exe\", \"%~dp0Git-2.17.0-32-bit.exe\")"
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
pip install asterisk-ami persist-queue selenium python-gettext pywin32
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
FOR /F "tokens=2 delims==" %%a IN ('wmic os get OSLanguage /Value') DO set OSLanguage=%%a
if "%OSLanguage%" == "1049" setx LANG ru

python c:\callcontrol\install\locales.py
rem if errorlevel 1 goto fail


echo install MicroSIP
rem TODO: use own .exe file
taskkill /f /im wscript.exe
taskkill /im MicroSIP.exe

start "Install MicroSIP" /wait "%~dp0MicroSIP-3.16.4.exe" /S
if errorlevel 1 goto fail
timeout 2
taskkill /im MicroSIP.exe
taskkill /f /im MicroSIP.exe
timeout 1

echo create shortcuts
c:\callcontrol\install\shortcuts.vbs

echo Part 2 OK
pause
exit 0

:fail
echo Error, run again
pause
exit 1

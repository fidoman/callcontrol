@echo off

if .%1 == .elevated goto elevated

set ME=%0
echo restart %ME%...
powershell -Command "Start-Process %ME% elevated -Verb RunAs"
if errorlevel 1 goto fail
exit 0

:elevated
echo elevated

echo installing python modules
pip install asterisk-ami
if errorlevel 1 goto fail

echo run configurator
python %~dp0microsipconf.py
if errorlevel 1 goto fail

echo install MicroSIP
%~dp0MicroSIP-3.15.7.exe /S
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
pause
exit 0

:fail
echo Error, run again
pause
exit 1

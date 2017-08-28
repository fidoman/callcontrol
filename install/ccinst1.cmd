@echo off

if .%1 == .elevated goto elevated

set ME=%0
echo restart %ME%...
powershell -Command "Start-Process %ME% elevated -Verb RunAs"
exit 0

:elevated
echo elevated

if exist %~dp0python-3.6.2.exe goto python_downloaded
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.python.org/ftp/python/3.6.2/python-3.6.2.exe\", \"%~dp0python-3.6.2.exe\")"
:python_downloaded
echo install python
%~dp0python-3.6.2.exe /passive InstallAllUsers=1 PrependPath=1 CompileAll=1

if exist %~dp0MicroSIP-3.15.7.exe goto microsip_downloaded
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://www.microsip.org/downloads/?file=MicroSIP-3.15.7.exe\", \"%~dp0MicroSIP-3.15.7.exe\")"
:microsip_downloaded
rem echo install MicroSIP
rem %~dp0MicroSIP-3.15.7.exe /S

if exist %~dp0Git-2.14.0.2-32-bit.exe goto git_downloaded
powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\"https://github.com/git-for-windows/git/releases/download/v2.14.0.windows.2/Git-2.14.0.2-32-bit.exe\", \"%~dp0Git-2.14.0.2-32-bit.exe\")"
:git_downloaded
echo install git
%~dp0Git-2.14.0.2-32-bit.exe /silent

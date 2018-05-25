set WshShell = CreateObject("WScript.Shell")

strPrograms = WshShell.SpecialFolders("Programs")
strStartup = WshShell.SpecialFolders("Startup")

set oMyShortCut= WshShell.CreateShortcut(strPrograms+"\Call Control Configuration.lnk")
oMyShortCut.WindowStyle = 7  'Minimized 0=Maximized  4=Normal 
'oMyShortcut.IconLocation = 
oMyShortCut.TargetPath = "pythonw.exe" 
oMyShortCut.Arguments = "c:\callcontrol\config.py"
oMyShortCut.WorkingDirectory = "c:\callcontrol"
oMyShortCut.Save



set oMyShortCut= WshShell.CreateShortcut(strStartup+"\Call Control.lnk")
oMyShortCut.WindowStyle = 7  'Minimized 0=Maximized  4=Normal 
'oMyShortcut.IconLocation = 
oMyShortCut.TargetPath = "python.exe" 
oMyShortCut.Arguments = "c:\callcontrol\callcontrol.py"
oMyShortCut.WorkingDirectory = "c:\callcontrol"
oMyShortCut.Save
'wscript.echo 1


microsiplnk = strStartup+"\MicroSIP.lnk"
Set fso = CreateObject("Scripting.FileSystemObject")
If (fso.FileExists(microsiplnk)) Then fso.DeleteFile(microsiplnk)

set oMyShortCut= WshShell.CreateShortcut(strStartup+"\MicroSIPRun.lnk")
oMyShortCut.WindowStyle = 7  'Minimized 0=Maximized  4=Normal 
'oMyShortcut.IconLocation = 
oMyShortCut.TargetPath = "wscript.exe" 
oMyShortCut.Arguments = "c:\callcontrol\microsiprun.vbs"
oMyShortCut.WorkingDirectory = "c:\callcontrol"
oMyShortCut.Save



'strDesktop = WshShell.SpecialFolders("Desktop")
'set oMyShortCut= WshShell.CreateShortcut(strDesktop+"\Dial.lnk")
'oMyShortCut.WindowStyle = 4
''oMyShortcut.IconLocation = 
'oMyShortCut.TargetPath = "pythonw.exe" 
'oMyShortCut.Arguments = "c:\callcontrol\dial.py"
'oMyShortCut.WorkingDirectory = "c:\callcontrol"
'oMyShortCut.Save

' TODO: replace microsip shortcut with microsiprun.vbs

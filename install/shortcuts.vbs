set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
set oMyShortCut= WshShell.CreateShortcut(strDesktop+"\Call Control.lnk")

oMyShortCut.WindowStyle = 7  'Minimized 0=Maximized  4=Normal 
'oMyShortcut.IconLocation = 
oMyShortCut.TargetPath = "pythonw.exe" 
oMyShortCut.Arguments = "c:\callcontrol\callcontrol.py"
oMyShortCut.WorkingDirectory = "c:\callcontrol"
oMyShortCut.Save

set oMyShortCut= WshShell.CreateShortcut(strDesktop+"\Dial.lnk")
oMyShortCut.WindowStyle = 4
'oMyShortcut.IconLocation = 
oMyShortCut.TargetPath = "pythonw.exe" 
oMyShortCut.Arguments = "c:\callcontrol\dial.py"
oMyShortCut.WorkingDirectory = "c:\callcontrol"
oMyShortCut.Save

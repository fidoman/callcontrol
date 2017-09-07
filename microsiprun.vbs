set WshShell = createobject("Wscript.Shell")


a=WshShell.RegRead("HKCR\MicroSIP\shell\open\command\")
'wscript.echo a
a=replace(a, """%1""", "")

while True
  WshShell.Run a, 2, True
wend


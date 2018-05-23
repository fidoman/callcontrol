import os
import sys
import subprocess

if os.name != "nt":
  exit()

langpath = os.path.join(sys.base_prefix, 'share', 'locale')
os.makedirs(langpath, exist_ok=True)
subprocess.Popen(["robocopy", "/e", "/r:0", "c:\\callcontrol\\i18n", langpath])

import os
import json

ASTERCONF = "asterisk.json"
asterdstpath = os.path.expandvars(r"%APPDATA%\callcontrol")

asterisk_conf = json.load(open(os.path.join(asterdstpath, ASTERCONF)))

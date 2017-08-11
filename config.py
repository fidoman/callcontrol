import os
import json

ASTERCONF = "asterisk.json"
datapath = os.path.expandvars(r"%APPDATA%\callcontrol")

asterisk_conf = json.load(open(os.path.join(datapath, ASTERCONF)))

call_log_dir = os.path.join(datapath, "calls")

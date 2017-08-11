import os
import json
import urllib.parse
import urllib.request

ASTERCONF = "asterisk.json"
datapath = os.path.expandvars(r"%APPDATA%\callcontrol")

asterisk_conf = json.load(open(os.path.join(datapath, ASTERCONF)))

call_log_dir = os.path.join(datapath, "calls")

def load_data(what):
  global asterisk_conf
  urlparams = urllib.parse.urlencode({'what': what, 'ext': asterisk_conf["ext"], 'pw': asterisk_conf["pw"]})

  resp = urllib.request.urlopen(asterisk_conf["data"]+"?"+urlparams)
  if resp.headers.get_content_type() != 'application/json':
    print("error:", repr(resp.read(1000)))
    raise Exception("server did not return JSON data")

  confdata = json.load(resp)

  return confdata

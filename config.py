import os
import json
import urllib.parse
import urllib.request

ASTERCONF = "asterisk.json"

#if os.uname().sysname=='Linux':
try:
  os.uname
  datapath = os.path.expandvars(r"$HOME/.callcontrol")
except:
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

  jsondata = resp.read()
  if type(jsondata)==bytes:
    jsondata=jsondata.decode("UTF-8") # python3.6 returns str, 3.5 does bytes

  confdata = json.loads(jsondata)

  return confdata

HELPWCONF = "helpwindow.json"

def read_help_window_conf():
  try:
    conf = json.load(open(os.path.join(datapath, HELPWCONF)))
  except:
    conf = { "x": 20, "y": 20, "w": 400, "h": 400 }
  return conf


def save_help_window_conf(c):
  json.dump(c, open(os.path.join(datapath, HELPWCONF), "w"))

def backend_query(what, params):
    global asterisk_conf
    cmd_params = urllib.parse.urlencode({'what': what, 'ext': asterisk_conf["ext"], 'pw': asterisk_conf["pw"]})
    data_params = urllib.parse.urlencode(params)
    url = asterisk_conf["data"] + "?" + cmd_params + "&" + data_params

    try:
      resp = urllib.request.urlopen(url)
      if resp.headers.get_content_type() != 'application/json':
        print("error:", repr(resp.read(1000)))
        raise Exception("server did not return JSON data")
      else:
        data = json.load(resp)
        return data

    except Exception as e:
      print(e)

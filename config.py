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
  
if os.path.exists(datapath) and not os.path.isdir(datapath):
  raise Exception("config path is not directory")
  
if not os.path.exists(datapath):
  os.makedirs(datapath, exist_ok=True)

aconf_filepath = os.path.join(datapath, ASTERCONF)

if not os.path.exists(aconf_filepath):
  print("no conf file, initializing")
  # no config or config does not have option "do not ask"
  asterisk_conf = {}
else:
  asterisk_conf = json.load(open(aconf_filepath))

if not asterisk_conf.get("do_not_ask", None) or __name__ == "__main__":
  print("reconfiguration")
  from ccconf import ask_config
  conf_upd, asterisk_conf = ask_config(asterisk_conf)
  print("Asterisk configuration:", asterisk_conf)

  if conf_upd:
    print("updating configs")
    with open(aconf_filepath, "w") as dst:
      json.dump(asterisk_conf, dst)


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
        data = json.loads(resp.read().decode("UTF-8"))
        return data

    except Exception as e:
      print(e)

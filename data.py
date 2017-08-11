#!/usr/bin/python3

import cgi
#import cgitb
import json
import sys
import postgresql
import traceback
import socket
import configparser

#cgitb.enable(display=0, logdir="/var/log/ccdata")

form = cgi.FieldStorage()



dbconn = json.load(open("database.json"))
db = postgresql.open(**dbconn)

def check_user(ext, pw):
  allowed = False
  for (c,) in db.prepare("select * from check_ext_pw($1, $2)")(ext, pw):
    if c==1:
      allowed = True
  if allowed:
    pass
  else:
    raise Exception("operator not found")




out = None

try:
  what = form.getvalue("what")
  ext = form.getvalue("ext")
  pw = form.getvalue("pw")
  check_user(ext, pw)

  if what == "shops":
    out=[]
    for n, ph, scr, ext in db.prepare("select shop_name, shop_phone, shop_script, myext from shops, sip_ext"
        " where phone=shop_phone")():
      out.append((n, ph, scr, ext))

  elif what == "tags":
    out=[]
    for i, t in db.prepare("select tag_id, tag_name from tags")():
      out.append((i, t))

  elif what == "config":
    out = {}
    out["name"] = socket.gethostname()
    out["manager_user"] = "callcontrol"

    conf = configparser.ConfigParser()
    conf.read("/etc/asterisk/manager.d/callcontrol.conf")
    out["manager_pw"] = conf['callcontrol']['secret']

    conf = configparser.ConfigParser()
    conf.read("/etc/asterisk/manager.conf")
    out["manager_host"] = socket.gethostname()
    out["manager_port"] = conf['general']['port']


except Exception as e:
  print("Content-type: text/plain\n")
  print("error:", str(e)) #, e.code, e.creator)
  #print(traceback.format_exc())
  exit()

print("Content-type: application/json\n")
json.dump(out, sys.stdout)

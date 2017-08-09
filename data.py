#!/usr/bin/python3

import cgi
import cgitb
import json
import sys
import postgresql
import traceback

cgitb.enable(display=0, logdir="/var/log/ccdata")

form = cgi.FieldStorage()



dbconn = json.load(open("database.json"))
db = postgresql.open(**dbconn)

def check_user(ext, pw):
  allowed = True
  for (c,) in db.prepare("select count(*) from extensions where ext_n=$1 and ext_pw=$2")(ext, pw):
    if c==1:
      allowed = True
  if allowed:
    pass
  else:
    raise Exception("operator not found")



what = form.getvalue("what")

out = None

try:
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
    ext = form.getvalue("ext")
    pw = form.getvalue("pw")
    check_user(ext, pw)
    out["name"] = ''

except Exception as e:
  print("Content-type: text/plain\n")
  print("error", type(e)) #, e.code, e.creator)
#  print(traceback.format_exc())
  exit()

print("Content-type: application/json\n")
json.dump(out, sys.stdout)

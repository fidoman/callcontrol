#!/usr/bin/python3

import cgi
#import cgitb
import json
import sys
import postgresql
import traceback
import socket
import configparser
import secrets

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

  elif what == "log_call":
    # save to database
    tag = form.get_value("tag")

    for (tag_id,) in db.prepare("select tag_id from tags where tag_name=$1"):
      break
    else:
      raise Exception("no such tag: "+repr(tag))

    operator = form.get_value("operator")
    op_id = int(operator)

    rec_uid = form.get_value("rec_uid")

    for _ in db.prepare("select rec_uid from call_log where cl_rec_uid=$1")(rec_uid):
      out = "Exists"
      break
    else:
      client_phone = form.get_value("client_phone")
      shop_phone = form.get_value("shop_phone")
      shop_name = form.get_value("shop_name")
      ring_time = form.get_value("ring_time")
      answer_time = form.get_value("answer_time")
      end_time = form.get_value("end_time")
      note = form.get_value("note")
      close_time = form.get_value("close_time")
    
      rand = secrets.token_urlsafe(32)
      db.prepare("insert into call_log ("
		"cl_rand, cl_tag, cl_operator, cl_rec_uid, cl_client_phone, cl_shop_phone, "
		"cl_shop_name, cl_ring_time, cl_answer_time, cl_end_time, cl_close_time, cl_note) "
		"values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)")\
	(rand, tag_id, op_id, rec_uid, client_phone, shop_phone, shop_name, ring_time, answer_time,
	end_time, close_time, note)

      out = "Added"

except Exception as e:
  print("Content-type: text/plain\n")
  print("error:", str(e)) #, e.code, e.creator)
  #print(traceback.format_exc())
  exit()

print("Content-type: application/json\n")
json.dump(out, sys.stdout)

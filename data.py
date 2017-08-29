#!/usr/bin/python3

import cgi
#import cgitb
import json
import sys
import postgresql
import traceback
import socket
import configparser
#import secrets
import itertools, random
import urllib.parse
from datetime import datetime

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
    tag = form.getvalue("tag")

    for (tag_id,) in db.prepare("select tag_id from tags where tag_name=$1")(tag):
      break
    else:
      raise Exception("no such tag: "+repr(tag))

    operator = form.getvalue("operator")
    for (op_id, op_name) in db.prepare("select op_id, op_name from operators where op_ext=$1")(operator):
      break
    else:
      op_id = op_name = None

    rec_uid = form.getvalue("rec_uid")

    for _ in db.prepare("select cl_rec_uid from call_log where cl_rec_uid=$1")(rec_uid):
      out = "Exists"
      break
    else:
      client_phone = form.getvalue("client_phone")
      shop_phone = form.getvalue("shop_phone")
      shop_name = form.getvalue("shop_name")
      ring_time = form.getvalue("ring_time")

      if ring_time == 'None': 
        ring_time = None
      else:
        ring_time = datetime.strptime(ring_time, '%Y-%m-%d %H:%M:%S.%f')

      answer_time = form.getvalue("answer_time")
      if answer_time == 'None': 
        answer_time = None
      else:
        answer_time = datetime.strptime(answer_time, '%Y-%m-%d %H:%M:%S.%f')

      end_time = form.getvalue("end_time")
      if end_time == 'None': 
        end_time = None
      else:
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')

      note = form.getvalue("note")

      close_time = form.getvalue("close_time")
      if close_time == 'None':
        close_time = None
      else:
        close_time = datetime.strptime(close_time, '%Y-%m-%d %H:%M:%S.%f')

      #rand = secrets.token_urlsafe(32)
      rand = ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') 
		for x in itertools.repeat(None, 32)])

#      raise Exception(repr(ring_time))

      db.prepare("insert into call_log ("
		"cl_rand, cl_tag, cl_operator, cl_operator_name, cl_rec_uid, cl_client_phone, cl_shop_phone, "
		"cl_shop_name, cl_ring_time, cl_answer_time, cl_end_time, cl_close_time, cl_note) "
		"values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)")\
	(rand, tag_id, op_id, op_name, rec_uid, client_phone, shop_phone, shop_name, ring_time, answer_time,
	end_time, close_time, note)

      out = "Added"

  elif what == "list_calls":
    """ show call_log table. Use ?what=get_rec&code=rand url's as links to records """
    print("Content-type: text/html; charset=utf-8\n")
    print('<table>')
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print('<thead style="background: lightgray;"><tr><td>Время записи</td><td>Магазин</td><td>Оператор</td><td>Клиент</td></tr></thead><tbody>')

    for (shop_name, operator_name, client_phone, close_time, rand) in db.prepare("select cl_shop_name, cl_operator_name, cl_client_phone, cl_close_time, cl_rand from call_log"):
      if rand:
        params = urllib.parse.urlencode({"what": "get_rec", "ext": ext, "pw": pw, "code": rand.strip()})
        a1 = "<a href=\"/cgi-bin/data.py?"+params+"\">"
        a2 = "</a>"
      else:
        a1=a2=''

      print(("<tr>""<td>"+a1+str(close_time or '')+a2+"</td><td>"+(shop_name or '')+"</td><td>"+(operator_name  or '')+"</td><td>"+(client_phone or '')+"</td>"+"</tr>"))

    print("</tbody></table>")
    exit()

  elif what == "get_rec":
    """ send audio file by code """
    for (rec_uid,) in db.prepare("select cl_rec_uid from call_log where cl_rand=$1")(form.getvalue("code")):
      import os
      out = [rec_uid]
      for x in os.walk("/var/spool/asterisk/monitor"):
        for fn in x[2]:
          if fn.find(rec_uid)!=-1:
            sys.stdout.buffer.write(b"Content-type: audio/wav\n\n")
            sys.stdout.buffer.write(open(os.path.join(x[0], fn), "rb").read())
            exit()
      break
    else:
      out = None

  elif what == "phone_history":
    """ get records for given phone order by date"""
    out = {}
    out["phone"] = form.getvalue("phone")
    out["list"] = []
    r = None
    for r in db.prepare("select call_log.*, tag_name from call_log, tags where cl_client_phone=$1 and cl_tag=tag_id order by cl_close_time desc")(out["phone"]):
#      r1 = [str(x) for x in r.values()]
      r1 = [str(x) if type(x)==datetime else x for x in r]
      out["list"].append(r1)
    if r: out["keymap"] = r.keymap

  elif what == "operators":
    out = {}
    out["list"] = []
    r = None
    for r in db.prepare("select * from operators")():
      r1 = [str(x) if type(x)==datetime else x for x in r]
      out["list"].append(r1)
    if r: out["keymap"] = r.keymap


except Exception as e:
  print("Content-type: text/plain\n")
  print("error:", str(e))
  print(traceback.format_exc())
  exit()

print("Content-type: application/json\n")
json.dump(out, sys.stdout)

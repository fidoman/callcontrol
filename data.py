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
from datetime import datetime, timezone
import os

#cgitb.enable(display=0, logdir="/var/log/ccdata")

form = cgi.FieldStorage()

def ext_from_channel(c):
  return "-".join(c.split("-")[:-1]) if type(c) is str else '-'


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


def my_url():
  return os.environ["REQUEST_SCHEME"]+"://"+os.environ["HTTP_HOST"]+os.environ["SCRIPT_NAME"]

def records_url():
  return os.environ["REQUEST_SCHEME"]+"://"+os.environ["HTTP_HOST"]+"/records/"


out = None

try:
 what = form.getvalue("what")

 # operations without auth

 if what == "get_rec":
    """ send audio file by code """
    disposition = form.getvalue("disposition")
    if disposition!="inline":
      disposition = "attachment"

    disposition+="; filename=\""+form.getvalue("code")+".wav\""

    for (rec_uid,) in db.prepare("select cl_rec_uid from call_log where cl_rand=$1")(form.getvalue("code")):
      import os
      out = [rec_uid]
      for x in os.walk("/var/spool/asterisk/monitor"):
        for fn in x[2]:
          if fn.find(rec_uid)!=-1:
            sys.stdout.buffer.write(b"Content-type: audio/wav\n")
            sys.stdout.buffer.write(b"Content-Disposition: "+disposition.encode("ascii")+b"\n")
            sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.write(open(os.path.join(x[0], fn), "rb").read())
            exit()
      break
    else:
      out = None

#  elif...

 else:
  # require auth

  ext = form.getvalue("ext")
  pw = form.getvalue("pw")
  check_user(ext, pw)

  if what == "shops":
    out=[]
    for n, ph, scr, ext, active, eid in db.prepare("select shop_name, shop_phone, shop_script, myext, shop_active, shop_eid from shops, sip_ext"
        " where phone=shop_phone")():
      out.append((n, ph, scr, ext, active, eid))

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

#    for _ in db.prepare("select cl_rec_uid from call_log where cl_rec_uid=$1")(rec_uid):
#      out = "Exists"
#      break
#    else:
    if True:
      client_phone = form.getvalue("client_phone")
      shop_phone = form.getvalue("shop_phone")
      shop_name = form.getvalue("shop_name")
      ring_time = form.getvalue("ring_time")

      if ring_time == 'None': 
        ring_time = None
      else:
        ring_time = datetime.strptime(ring_time, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

      answer_time = form.getvalue("answer_time")
      if answer_time == 'None': 
        answer_time = None
      else:
        answer_time = datetime.strptime(answer_time, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

      end_time = form.getvalue("end_time")
      if end_time == 'None': 
        end_time = None
      else:
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

      note = form.getvalue("note")
      order = form.getvalue("order")

      close_time = form.getvalue("close_time")
      if close_time == 'None':
        close_time = None
      else:
        close_time = datetime.strptime(close_time, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

      #rand = secrets.token_urlsafe(32)
      rand = ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') 
		for x in itertools.repeat(None, 32)])

#      raise Exception(repr(ring_time))

      uid = form.getvalue("uid")
      direction = form.getvalue("direction")

      db.prepare("insert into call_log ("
		"cl_rand, cl_tag, cl_operator, cl_operator_name, cl_rec_uid, cl_client_phone, cl_shop_phone, "
		"cl_shop_name, cl_ring_time, cl_answer_time, cl_end_time, cl_close_time, cl_note, cl_order, cl_uid, cl_direction) "
		"values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16) "
		"on conflict (cl_uid) do "
		"update set (cl_rand, cl_tag, cl_operator, cl_operator_name, cl_rec_uid, cl_client_phone, cl_shop_phone, "
		"cl_shop_name, cl_ring_time, cl_answer_time, cl_end_time, cl_close_time, cl_note, cl_order, cl_direction) = "
		"(EXCLUDED.cl_rand, EXCLUDED.cl_tag, EXCLUDED.cl_operator, EXCLUDED.cl_operator_name, EXCLUDED.cl_rec_uid, "
		"EXCLUDED.cl_client_phone, EXCLUDED.cl_shop_phone, "
		"EXCLUDED.cl_shop_name, EXCLUDED.cl_ring_time, EXCLUDED.cl_answer_time, EXCLUDED.cl_end_time, "
		"EXCLUDED.cl_close_time, EXCLUDED.cl_note, EXCLUDED.cl_order, EXCLUDED.cl_direction)")\
	(rand, tag_id, op_id, op_name, rec_uid, client_phone, shop_phone, shop_name, ring_time, answer_time,
	end_time, close_time, note, order, uid, direction)
#	(rand, tag_id, op_id, op_name, rec_uid, client_phone, shop_phone, shop_name, ring_time.astimezone(tz=None), answer_time.astimezone(tz=None),
#	end_time.astimezone(tz=None), close_time.astimezone(tz=None), note, order, uid, direction)

      out = {"status": "added"}

  elif what == "list_calls":
    """ show call_log table. Use ?what=get_rec&code=rand url's as links to records """
    print("Content-type: text/html; charset=utf-8")
    print()
    print('<table>')
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print('<thead style="background: gray;"><tr><th>Время завершения</th><th>Магазин</th><th>Оператор</th><th>Клиент</th><th>Дозвон</th><th>Тэг</th><th>Запись</th></tr></thead><tbody>')

    odd = True

    for (shop_name, operator_name, client_phone, close_time, rand, tag, answer_time) in db.prepare("select cl_shop_name, cl_operator_name, cl_client_phone, cl_close_time, cl_rand, tag_name, cl_answer_time from call_log, tags where tag_id=cl_tag order by cl_close_time"):
      if rand:
        params_att = urllib.parse.urlencode({"what": "get_rec", "disposition": "attachment", "code": rand.strip()})
        params_inl = urllib.parse.urlencode({"what": "get_rec", "disposition": "inline", "code": rand.strip()})
        rec_url_att = my_url()+"?"+params_att
        rec_url_inl = my_url()+"?"+params_inl
        a1_att = "<a href=\""+ rec_url_att +"\">"
        a2_att = "</a>"
        a1_inl = '<audio controls style="height:26pt;"> <source src="'+ rec_url_inl +'" type="audio/wav">'
        a2_inl = "</audio>"
      else:
        a1=a2=''

      if type(close_time) is datetime:
        close_time_str = close_time.strftime("%Y-%m-%d %H:%M:%S")
      else:
        close_time_str = ''

      print((("<tr>" if odd else '<tr style="background:lightgray;">') + "<td>"+close_time_str+"</td><td>"+(shop_name or '')+"</td><td>"+(operator_name  or '')+"</td><td>"+(client_phone or '')+"</td>"+\
	    "<td>"+("Да" if answer_time else "Нет")+"</td>" +\
	    "<td>"+(tag or '')+"</td>" +\
	    "<td>"+a1_att+"Скачать"+a2_att +" " + a1_inl+"Прослушать"+a2_inl+"</td>" +\
	    "</tr>"))

      odd = not odd

    print("</tbody></table>")
    exit()


  elif what == "list_calls2":
    """ show call_log table. Use ?what=get_rec&code=rand url's as links to records """
#    print("Content-type: text/html; charset=utf-8")
#    print()
#    print('<table>')
#    import codecs
#    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

#    print('<thead style="background: gray;"><tr><th>Время завершения</th><th>Магазин</th><th>Оператор</th><th>Клиент</th><th>Дозвон</th><th>Тэг</th><th>Запись</th></tr></thead><tbody>')

#    odd = True

    out = []
    for (shop_name, operator_name, direction, client_phone, close_time, 
         rand, tag, answer_time, order) in db.prepare("select cl_shop_name, cl_operator_name, cl_direction, cl_client_phone, cl_close_time, cl_rand, tag_name, cl_answer_time, cl_order from call_log, tags where tag_id=cl_tag order by cl_close_time"):
      if rand:
        params_att = urllib.parse.urlencode({"what": "get_rec", "disposition": "attachment", "code": rand.strip()})
        params_inl = urllib.parse.urlencode({"what": "get_rec", "disposition": "inline", "code": rand.strip()})
        rec_url_att = my_url()+"?"+params_att
        rec_url_inl = my_url()+"?"+params_inl
        a1_att = "<a href=\""+ rec_url_att +"\">"
        a2_att = "</a>"
        a1_inl = '<audio controls style="height:26pt;"> <source src="'+ rec_url_inl +'" type="audio/wav">'
        a2_inl = "</audio>"
      else:
        rec_url_att = ''
        rec_url_inl = ''
        a1=a2=''

      if type(close_time) is datetime:
        close_time_str = close_time.astimezone().strftime("%Y-%m-%d %H:%M:%S") # better use client's timezone
      else:
        close_time_str = ''

#      print((("<tr>" if odd else '<tr style="background:lightgray;">') + "<td>"+close_time_str+"</td><td>"+(shop_name or '')+"</td><td>"+(operator_name  or '')+"</td><td>"+(client_phone or '')+"</td>"+\
#	    "<td>"+("Да" if answer_time else "Нет")+"</td>" +\
#	    "<td>"+(tag or '')+"</td>" +\
#	    "<td>"+a1_att+"Скачать"+a2_att +" " + a1_inl+"Прослушать"+a2_inl+"</td>" +\
#	    "</tr>"))
      out.append({"close_time": close_time_str,
                  "shop_name": shop_name or '',
                  "operator_name": operator_name  or '',
                  "direction": direction or '',
                  "client_phone": client_phone or '',
                  "answered": "Да" if answer_time else "Нет",
                  "tag": tag or '',
                  "order": order or '',
                  "rec_url_att": rec_url_att,
                  "rec_url_inl": rec_url_inl
      })

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport"
     content="width=device-width, initial-scale=1, user-scalable=yes">
  <title>Calls</title>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
  <script>
  angular.module('TableFilterApp', [])
    .controller('TableFilterController', function($scope) {
      $scope.calls = """ + json.dumps(out) + """;
    });
  </script>
</head>

<body ng-app="TableFilterApp" ng-controller="TableFilterController">

<table>
<tr><th>Время завершения</th><th>Магазин</th><th>Оператор</th><th>Направление</th><th>Клиент</th><th>Заказ</th><th>Дозвон</th><th>Тэг</th><th>Запись</th></tr>
<tr>
  <td><input ng-model="f.close_time"></td>
  <td><input ng-model="f.shop_name"></td>
  <td><input ng-model="f.operator_name"></td>
  <td><input ng-model="f.direction"></td>
  <td><input ng-model="f.client_phone"></td>
  <td><input ng-model="f.order"></td>
  <td><input ng-model="f.answered"></td>
  <td><input ng-model="f.tag"></td>
  <td></td>
</tr>
<tr ng-repeat="c in calls | filter:f">
  <td>{{c.close_time}}</td>
  <td>{{c.shop_name}}</td>
  <td>{{c.operator_name}}</td>
  <td>{{c.direction}}</td>
  <td>{{c.client_phone}}</td>
  <td>{{c.order}}</td>
  <td>{{c.answered}}</td>
  <td>{{c.tag}}</td>
  <td><a href="{{c.rec_url_att}}">Скачать</a>
      <audio controls style="height:26pt;"> <source src="{{c.rec_url_inl}}" type="audio/wav"></audio></td>
</tr>
</table>
</body>
</html>
"""

    print("Content-type: text/html; charset=utf-8")
    print()
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print(doc)

    exit()


  elif what == "list_cdr":
    out = []
    for (calldate, clid, src, dst, dcontext, channel, dstchannel, lastapp, lastdata, duration, billsec, disposition, amaflags, accountcode, uniqueid, userfield, recordingfile, tag_name, cl_order, cl_operator_name, cl_direction) in \
        db.prepare("select calldate, clid, src, dst, dcontext, channel, dstchannel, lastapp, lastdata, duration, billsec, disposition, amaflags, accountcode, uniqueid, userfield, recordingfile, tag_name, cl_order, cl_operator_name, cl_direction from "
                   "cdr left outer join call_log on (uniqueid=cl_uid) left outer join tags on (cl_tag=tag_id) order by calldate desc"):

      if type(calldate) is datetime:
        calldate_str = calldate.strftime("%Y-%m-%d %H:%M:%S")
      else:
        calldate_str = ''

#      print((("<tr>" if odd else '<tr style="background:lightgray;">') + "<td>"+close_time_str+"</td><td>"+(shop_name or '')+"</td><td>"+(operator_name  or '')+"</td><td>"+(client_phone or '')+"</td>"+\
#	    "<td>"+("Да" if answer_time else "Нет")+"</td>" +\
#	    "<td>"+(tag or '')+"</td>" +\
#	    "<td>"+a1_att+"Скачать"+a2_att +" " + a1_inl+"Прослушать"+a2_inl+"</td>" +\
#	    "</tr>"))
      out.append({
		"calldate": calldate_str, 
		"clid": clid,
		"src": src,
		"dst": (dst or '')+"@"+(dcontext or''),
#		"dcontext": dcontext, 
		"channel": channel, 
		"dstchannel": dstchannel,
		"lastapp": str(lastapp)+"/"+str(lastdata),
#	"lastdata": lastdata, 
		"duration": duration, 
		"billsec": billsec,
		"disposition": disposition,
		"uniqueid": uniqueid, 
		"amaflags": amaflags,
		"accountcode": accountcode,
		"uniqueid": uniqueid,
		"userfield": userfield, 
		"recordingfile": recordingfile+".wav" if recordingfile else "about:blank",
                "tag_name": tag_name,
                "cl_order": cl_order,
                "cl_direction": cl_direction,
                "cl_operator_name": cl_operator_name or ext_from_channel(channel if dst and dst.startswith("+") else dstchannel),
      })


    docfields=[
	("Дата", "calldate"),
	("Тип", "cl_direction"),
	("CallerID", "clid"),
	("Вызывающий", "src"),
        ("Вызываемый", "dst"),
	("Тэг", "tag_name"),
	("Заказ", "cl_order"),
	("Оператор", "cl_operator_name"),
#       ("Канал", "channel"),
#        ("Канал назначения", "dstchannel"),
#("Вызов", "lastapp"),
	("Секунды всего", "duration"),
	("Секунды разговора", "billsec"),
	("Результат", "disposition"),
	("Запись", "recordingfile"),
    ]


    doc = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport"
     content="width=device-width, initial-scale=1, user-scalable=yes">
  <title>CDR</title>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
  <script>
  angular.module('TableFilterApp', [])
    .controller('TableFilterController', function($scope) {
      $scope.calls = """ + json.dumps(out) + """;
    });
  </script>
</head>

<body ng-app="TableFilterApp" ng-controller="TableFilterController">

<div style="white-space: nowrap;">
<table>
<tr>"""+"".join(["<th align=left>"+x[0]+"</th>" for x in docfields])+"""</tr>
<tr>"""+"".join(['<td><input ng-model="f.'+x[1]+'"></td>' for x in docfields])+"""</tr>
<tr ng-repeat="c in calls | filter:f">"""+\
  " ".join([("<td>{{c."+x[1]+"}}</td>" if x[1]!="recordingfile" else '<td><a href="'+records_url()+'{{c.recordingfile}}">Запись</a></td>') for x in docfields])+\
"""
</tr>
</table>
</div>
</body>
</html>
"""

    print("Content-type: text/html; charset=utf-8")
    print()
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print(doc)
    exit()




  elif what == "phone_history":
    """ get records for given phone order by date"""
    out = {}
    phone = out["phone"] = form.getvalue("phone")
    shop = out["shop"] = form.getvalue("shop")
    out["list"] = []
    r = None
    for r in db.prepare("select call_log.*, tag_name from call_log, tags where cl_client_phone=$1 and cl_shop_name=$2 and cl_tag=tag_id order by cl_close_time desc")(phone, shop):
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


  elif what == "new_order":
    out = { "order_id": "-1", "order_url": "about:blank" }

  elif what == "list_orders":
    out = { "order_id": "-1", "order_url": "about:blank" }


except Exception as e:
  print("Content-type: text/plain\n")
  print("error:", str(e))
  print(traceback.format_exc())
  exit()

print("Content-type: application/json\n")
json.dump(out, sys.stdout)

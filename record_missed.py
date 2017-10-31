#!/usr/bin/python3

import sys
import json
import postgresql
from datetime import datetime
from datetime import timezone

dbconn = json.load(open("/opt/asterisk/database.json"))
db = postgresql.open(**dbconn)

tmstmp = datetime.utcnow().replace(tzinfo=timezone.utc)

out=open("/tmp/loghangup", "a")
out.write(str(tmstmp) + ' ' + repr(sys.argv) + '\n')

cl_phone = sys.argv[2]
ext = sys.argv[3]
cl_uid = sys.argv[5]

try: 
  q1 = db.prepare("select shop_phone, shop_name from shops join sip_ext on (phone=shop_phone) where myext=$1")
  for (shop_phone, shop_name) in q1(ext):
    q2=db.prepare("insert into call_log (cl_tag, cl_client_phone, cl_shop_phone, cl_shop_name, cl_ring_time, cl_end_time, cl_close_time, cl_direction, cl_uid)"
        " values (3, $1, $2, $3, $4, $4, $4, 'incoming', $5) on conflict (cl_uid) do nothing")
    q2(cl_phone, shop_phone, shop_name, tmstmp, cl_uid)
    break
except Exception as e:
  out.write("error\n")
  out.write(str(e)+"\n")


#cl_tag=3
#cl_client_phone=
#cl_shop_phone=
#cl_shop_name=
#cl_ring_time= 
#cl_end_time=
#cl_close_time=
#cl_direction='incoming'

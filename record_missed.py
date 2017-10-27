#!/usr/bin/python3

import postgresql

dbconn = json.load(open("database.json"))
db = postgresql.open(**dbconn)

#cl_tag=3
#cl_client_phone=
#cl_shop_phone=
#cl_shop_name=
#cl_ring_time= 
#cl_end_time=
#cl_close_time=
#cl_direction='incoming'

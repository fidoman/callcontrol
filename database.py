import json
import postgresql
import random
import re
from itertools import count
import urllib.parse
import urllib.request

""" 
Module for database access
1. Updates:
     store in local queue
     upload as soon as possible
2. Queries:
     online

Keep connection, reestablish if needed
"""     

#def save_record(r):
  

#def get_call_history(callerid):
#  ...

#class CallsDB():
#  def __init__(self):
#    self.conndata=

PWsym="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-+.,[]{}()`~!?@#$%^&*/_="
def gen_pw(l):
  s=""
  for z in range(l):
    s+=PWsym[random.randrange(0,len(PWsym))]
  return s

def load_operators():
    ops = {}
    for op_name, op_ext in db.prepare("select op_name, op_ext from operators"):
      ops[op_name] = op_ext
    return ops

def l1_queue(op1, op2):
    members = [x for x in (op1, op2) if x]
    members.sort()
    qname = "_".join((["l1"]+members))
    return members, qname


days={
'пн': 'mon',
'вт': 'tue',
'ср': 'wed',
'чт': 'thu',
'пт': 'fri',
'сб': 'sat',
'вс': 'sun'
}

if __name__=="__main__":
  import sys

  if len(sys.argv)<2:
    print("nothing to do")
    exit()

  dbconn = json.load(open("database.json"))
  db = postgresql.open(**dbconn)

  if sys.argv[1]=="passwords":
    """ populate and show passwords for operators """
    for ext, name in db.prepare("select op_ext, op_name from operators")():
      if not ext: continue
      pw = db.prepare("select ext_pw from extensions where ext_n=$1")(ext)
      if len(pw)==0:
        print("generate password for", ext)
        npw = gen_pw(12)
        db.prepare("insert into extensions (ext_n, ext_pw) values ($1, $2)")(ext, npw)
      else:
        npw = pw[0][0]
      print("%s;%s;%s"%(name, ext, npw))

  elif sys.argv[1]=="rmpw":
    if len(sys.argv)<3:
      print("specify extensions")
      exit()
    for ext in sys.argv[2:]:
      db.prepare("delete from extensions where ext_n=$1")(ext)

  elif sys.argv[1]=="operators":
    print("; sip.conf part for opeartors")
    TPL="""
[%(ext)s]
transport=tls
encryption=no
type=friend
context=from-internal
username=%(ext)s
secret=%(secret)s
host=dynamic
nat=force_rport,comedia
qualify=yes
canreinvite=no
;callgroup=1
;pickupgroup=1
call-limit=1
dtmfmode=auto
disallow=all
allow=alaw
allow=ulaw
allow=g729
allow=g723
allow=g722
outofcall_message_context=intmsg
"""
    for n, pw in db.prepare("select ext_n, ext_pw from extensions order by ext_n"):
      print(TPL%{"ext": n, "secret": pw})

  elif sys.argv[1]=="sipout":
    print("; sip.conf part for provider")
    TPL="""
[sipout%(prov_ext)s]
type=peer
username=%(prov_name)s
secret=%(prov_secret)s
dtmfmode=rfc2833
context=trunkinbound
insecure=port,invite
host=%(prov_host)s
"""
    for su_host, su_username, su_secret, su_myext in db.prepare("select su_host, su_username, su_secret, su_myext from sip_users"):
      print(TPL%{"prov_ext": su_myext, "prov_name": su_username, "prov_secret": su_secret, "prov_host": su_host})

  elif sys.argv[1]=="sipout-register":
    TPL="""register => %(sipuser)s:%(sippw)s@%(host)s/%(myext)s"""
    for su_host, su_username, su_secret, su_myext in db.prepare("select su_host, su_username, su_secret, su_myext from sip_users"):
      print(TPL%{"myext": su_myext, "sipuser": su_username, "sippw": su_secret, "host": su_host})

  elif sys.argv[1]=="callout":
    print("; callout part of extensions.conf")
    TPL="exten => _+7XXXXXXXXXX/%(prov_phone)s,5,Dial(SIP/sipout%(prov_ext)s/7${EXTEN:2},,To)\n"
    for su_username, su_myext, su_phone in db.prepare("select su_username, su_myext, su_phone from sip_users"):
      print(TPL%{"prov_phone": su_phone, "prov_ext": su_myext})

  elif sys.argv[1]=="internal":
    print("; internal extensions")
    TPL="""exten => %(ext)s,1,Dial(SIP/%(ext)s,,ti)
exten = %(ext)s,hint,SIP/%(ext)s"""
    for (n,) in db.prepare("select ext_n from extensions order by ext_n"):
      print(TPL%{"ext": n})

  elif sys.argv[1]=="inbound":
    print("""; inbound calls
; if shop is active
; use 3 dial commands in order
; then goto voicemail

; if shop is not active - play sound
; 
""")
    

    ops = load_operators()

    TPL="""
exten => %(prov_ext)s,1,System(/usr/local/bin/log_call.py h:%(sip_host)s e:${EXTEN} u:${UNIQUEID} cid:${CALLERID(num)} dialp:${DIALEDPEERNUMBER} dnid:${DNID})
exten => %(prov_ext)s,n,Set(CALLERID(num)=+${CALLERID(num)})
exten => %(prov_ext)s,n,Monitor(wav,callin-%(prov_ext)s-${CHANNEL}--${UNIQUEID}--${CALLERID(num)}--${EXTEN},m)
exten => %(prov_ext)s,n,Set(CDR(recordingfile)=callin-%(prov_ext)s-${CHANNEL}--${UNIQUEID}--${CALLERID(num)}--${EXTEN})
exten => %(prov_ext)s,n,Set(CALLERID(name)=%(destiname)s)
exten => %(prov_ext)s,n,Set(CHANNEL(hangup_handler_push)=inbound-hangup,s,1(${CALLERID(num)},%(sip_host)s,${EXTEN},${HANGUPCAUSE},${UNIQUEID}))
%(dial)s
exten => %(prov_ext)s,n,Voicemail(%(prov_ext)s@missed)
;exten => %(prov_ext)s,n,Set(CHANNEL(hangup_handler_pop)=)
exten => %(prov_ext)s,n,Hangup
    """

    def mk_dial(dest, pri, exts, timeout):
      if exts:
        dial = "&".join(["SIP/%s"%x for x in exts if x])
        return "exten => %s,%s,Dial(%s,%d,ti)\n"%(dest, pri, dial, timeout)
      return ''

    def mk_queue(dest, pri, qname, timeout, is_first):
      return "exten => %s,%s,Queue(%s,,,,%d)\n"%(dest, pri+"(xx_start_ring)" if is_first else pri, qname, timeout) + \
             "exten => %s,n,Wait(1)\n"%dest

    def get_group(ext):
      """  """
      for (e,) in db.prepare("select op2.op_ext from operators op1, operators op2 where op1.op_group=op2.op_group and op1.op_ext=$1")(ext):
        yield e

    def get_group_n(n):
      """  """
      for (e,) in db.prepare("select op_ext from operators where op_group=$1")(n):
        yield e

    def get_all():
      for (e,) in db.prepare("select op_ext from operators where op_group is not null")():
        yield e

    def get_neighbours(ext, which):
      if which=="все":
        exts = set(get_all())
      elif which=="ячейка ПМ":
        exts = set(get_group(ext))
      elif which.startswith("ячейка "):
        n=which[7:]
        exts = set(get_group_n(n))
      else:
        exts = set()
      return exts

    def get_groupname(m1, m2, which):
      if which=="все":
        return "l3"
      elif which=="ячейка ПМ":
        for (g,) in db.prepare("select op_group from operators where op_ext=$1 or op_ext=$2 limit 1")(m1, m2):
          return "l2_"+g
        return None
      elif which.startswith("ячейка "):
        n=which[7:]
        return "l2_"+n
      else:
        return None

    processed_phones = {}
    # get extensions
    for shop_name, shop_phone, shop_active, su_host, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, worktime in db.prepare("select shop_name, shop_phone, shop_active, su_host, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, l_worktime from shops, sip_users, levels where su_phone=shop_phone and l_name=shop_level order by su_myext"):
      if shop_phone in processed_phones:
        print("; duplicate phone", shop_phone, shop_name, processed_phones[shop_phone])
        continue
      else:
        processed_phones[shop_phone] = shop_name

      print("; ", repr(shop_name), su_myext, repr(worktime))
      if shop_active != "Да":
        #print(shop_name, "is disabled")
        dial = """exten => %(ext)s,n,Answer()
exten => %(ext)s,n,Morsecode(account is locked)
"""%{"ext": su_myext}
      else:

        dial = ''
        ###
        #worktime = 'пн-ср 01:00-22:00'

        if not worktime: # empty value
          dial+="; no limits on worktime\n"
          dial+="exten => %s,n,Goto(start_ring)\n"%su_myext

        else:
          m_timerange = re.match("(\d\d:\d\d-\d\d:\d\d)$", worktime)
          if m_timerange:
            print("; just time")
            dial+="exten => %s,n,GotoIfTime(%s,,,?start_ring)\n"%(su_myext, worktime)

          else:
            print("; worktime by days of week")
            re_worktime=re.compile("(пн|вт|ср|чт|пт|сб|вс)(-(пн|вт|ср|чт|пт|сб|вс))?(\s+(\d\d:\d\d-\d\d:\d\d))?\s*(.*)$", re.I + re.MULTILINE)
            worktime=worktime.replace("\n", " ")
            while True:
              m = re_worktime.match(worktime)
              if not m:
                break
              day1 = m.group(1)
              day2 = m.group(3)
              timerange = m.group(5)

              dial+="exten => %s,n,GotoIfTime(%s,%s,,?start_ring)\n"%(su_myext, timerange, days[day1]+("-" + days[day2] if day2 else ''))

              tail = m.group(6)
              worktime=tail

        dial += "exten => %s,n,Voicemail(%s@offtime,u)\n"%(su_myext, su_myext)
        dial += "exten => %s,n,Hangup\n"%su_myext

        phases = []
        m1 = ops.get(shop_manager)
        m2 = ops.get(shop_manager2)
        if m1 or m2:
          print("; phase1: personal managers:", m1, m2)
          _, qname = l1_queue(m1, m2)
          phases.append(qname)
        #dial = mk_dial(su_myext, "n", (m1, m2))

        if shop_queue2:
          print("; phase2:", shop_queue2)
#          phases.append(list(get_neighbours(m1, shop_queue2) | get_neighbours(m2, shop_queue2)))
          qname = get_groupname(m1, m2, shop_queue2)
          phases.append(qname)

#        dial += mk_dial(su_myext, "n", list(q2))

        if shop_queue3:
          print("; phase3:", shop_queue3)
          qname = get_groupname(m1, m2, shop_queue3)
          phases.append(qname)
#          phases.append(list(get_neighbours(m1, shop_queue3) | get_neighbours(m2, shop_queue3)))
#        dial += mk_dial(su_myext, "n", list(q3))


        dial += "exten => %s,n(start_ring),Verbose(0,Start Ring %s - log)\n"%(su_myext, su_myext)

        for ph, n in zip(phases, count()):
          last_iter = n==len(phases)-1
          print(";", n, ph, last_iter)
#          dial += mk_dial(su_myext, "n", ph, 120 if last_iter else 15)
          dial += mk_queue(su_myext, "n", ph, 120 if last_iter else 15, n==0)

#        print(phases); exit()

      print(TPL%{'prov_ext':su_myext, 'destiname':shop_name, 'dial': dial, 'sip_host': su_host})

  elif sys.argv[1]=="queues":
    # make queues:

    # level_1 - walk shops and make for all used PM's combinations
    queues = {}
    ops = load_operators()
    for shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, worktime in db.prepare("select shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, l_worktime from shops, sip_users, levels where su_phone=shop_phone and l_name=shop_level order by su_myext"):
      if shop_active=="Да":
        op1 = ops.get(shop_manager)
        op2 = ops.get(shop_manager2)
        if not op1 and not op2: continue
        members, qname = l1_queue(op1, op2)
        queues[qname] = members
    #print(queues)

    # level_2 - all groups
    groups = {} # group -> members
    all_ops = []
    for op_ext, op_group in db.prepare("select op_ext, op_group from operators where op_group is not null"):
      #print(op_ext,op_group)
      groups.setdefault(op_group, []).append(op_ext)
      all_ops.append(op_ext)
    #print(groups)
    for grp_n, grp_memb in groups.items():
      queues["l2_"+grp_n] = grp_memb

    # level_3 - everybody
    queues["l3"] = all_ops

    for q, m in queues.items():
      print("[%s]"%q)
      print("strategy = ringall")
      for m1 in m:
        print("member = SIP/%s"%m1)

  elif sys.argv[1]=="voicemail":
    # configure vicemail for shops
    print("; voicemail")

    print()
    print("; offtime calls")
    print("[offtime]")
    for shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, worktime in db.prepare("select shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, l_worktime from shops, sip_users, levels where su_phone=shop_phone and l_name=shop_level order by su_myext"):
      print(su_myext, "=>", "xxxxpwpwpw,"+shop_name+","+"sergey@fidoman.ru"+",,attach=yes|delete=1|emailsubject=Offtime call from ${VM_CALLERID}")

    print()
    print("; missed calls")
    print("[missed]")
    for shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, worktime in db.prepare("select shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3, l_worktime from shops, sip_users, levels where su_phone=shop_phone and l_name=shop_level order by su_myext"):
      print(su_myext, "=>", "xxxxpwpwpw,"+shop_name+","+"sergey@fidoman.ru"+",,attach=yes|delete=1|emailsubject=Missed call from ${VM_CALLERID}")

  elif sys.argv[1]=="load_shop_ids":
    queries = json.load(open("lk.json"))
    for (shop_name,) in db.prepare("select shop_name from shops"):
      url=queries["shop_id"]%{"shop_name": urllib.parse.quote(shop_name)}
      try:
        resp = urllib.request.urlopen(url)
        if resp.headers.get_content_type() != 'application/json':
          print("error:", repr(resp.read(1000)))
          raise Exception("server did not return JSON data")
        else:
          data = json.loads(resp.read().decode("utf-8"))
          print(shop_name, len(data['items']))

      except Exception as e:
        print(e)

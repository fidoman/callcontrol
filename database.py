import json
import postgresql
import random

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
      pw = db.prepare("select ext_pw from extensions where ext_n=$1")(ext)
      if len(pw)==0:
        print("generate password for", ext)
        npw = gen_pw(12)
        db.prepare("insert into extensions (ext_n, ext_pw) values ($1, $2)")(ext, npw)
      else:
        npw = pw[0][0]
      print("%40s %05s %16s"%(name, ext, npw))

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
nat=comedia
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
    TPL="exten => _+7XXXXXXXXXX/%(prov_phone)s,3,Dial(SIP/sipout%(prov_ext)s/7${EXTEN:2},,To)\n"
    for su_username, su_myext, su_phone in db.prepare("select su_username, su_myext, su_phone from sip_users"):
      print(TPL%{"prov_phone": su_phone, "prov_ext": su_myext})

  elif sys.argv[1]=="internal":
    print("; internal extensions")
    TPL="""exten => %(ext)s,1,Dial(SIP/%(ext)s,,To)
exten = %(ext)s,hint,SIP/%(ext)s"""
    for (n,) in db.prepare("select ext_n from extensions order by ext_n"):
      print(TPL%{"ext": n})

  elif sys.argv[1]=="inbound":
    print(";inbound calls")

    ops = {}
    for op_name, op_ext in db.prepare("select op_name, op_ext from operators"):
      ops[op_name] = op_ext

    TPL="""
exten => %(prov_ext)s,1,Set(CALLERID(num)=+${CALLERID(num)})
exten => %(prov_ext)s,2,Monitor(wav,callin-%(prov_ext)s-${CHANNEL}--${UNIQUEID}--${CALLERID(num)}--${EXTEN},m)
exten => %(prov_ext)s,3,Set(CALLERID(name)=%(destiname)s)
;exten => %(prov_ext)s,n,Dial(SIP/)
%(dial)s
; call primary manager
; then call group
exten => %(prov_ext)s,n,Hangup
    """

    def mk_dial(dest, pri, exts):
      if exts:
        dial = "&".join(["SIP/%s"%x for x in exts if x])
        return "exten => %s,%s,Dial(%s,15,o)\n"%(dest, pri, dial)
      return ''


    # get extensions
    for shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3 in db.prepare("select shop_name, shop_phone, shop_active, su_myext, shop_manager, shop_manager2, shop_queue2, shop_queue3 from shops, sip_users where su_phone=shop_phone order by su_myext"):
      print("; ", shop_name, su_myext)
      if shop_active != "Да":
        #print(shop_name, "is disabled")
        dial = """exten => %(ext)s,n,Answer()
exten => %(ext)s,n,Morsecode(account is locked)
"""%{"ext": su_myext}
      else:
        dial = mk_dial(su_myext, "n", (ops.get(shop_manager), ops.get(shop_manager2)))

      print(TPL%{'prov_ext':su_myext, 'destiname':shop_name, 'dial': dial})

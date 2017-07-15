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

PWsym="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-+.,<>[]{}()`~!?@#$%^&*/_="
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
    for (ext,) in db.prepare("select op_ext from operators")():
      pw = db.prepare("select ext_pw from extensions where ext_n=$1")(ext)
      if len(pw)==0:
        print("generate password for", ext)
        pw = gen_pw(12)
        db.prepare("insert into extensions (ext_n, ext_pw) values ($1, $2)")(ext, pw)

  elif sys.argv[1]=="rmpw":
    if len(sys.argv)<3:
      print("specify extensions")
      exit()
    for ext in sys.argv[2:]:
      db.prepare("delete from extensions where ext_n=$1")(ext)

import os
import sys
import urllib.request
import urllib.parse
import json
from tkinter import *

#dstpath = os.path.expandvars(r"%APPDATA%\MicroSIP")
#srcpath = os.path.dirname(sys.argv[0])
#CONF = "microsip.ini"

def save(root, x):
  str_srv = x[1].get()
  str_ext = x[2].get()
  str_pw = x[3].get()
  int_dna = x[4].get()
  if not str_srv or not str_ext or not str_pw:
    root.bell()
    return

  q_url="https://"+str_srv+"/cgi-bin/data.py"

  # urlencode ext and pw
  urlparams = urllib.parse.urlencode({'what': 'config', 'ext': str_ext, 'pw': str_pw})

  resp = urllib.request.urlopen(""+q_url+"?"+urlparams+"")
  if resp.headers.get_content_type() != 'application/json':
    print("error:", repr(resp.read(1000)))
    root.bell()
    return
  print(resp.headers)
  jsondata = resp.read().decode('ascii')
  print(jsondata)
  confdata = json.loads(jsondata)
  print(confdata)

  # get manager user/pass from server
  #os.makedirs(dstpath, exist_ok = True)
  #tpl = open(os.path.join(srcpath, CONF)).read()
  #conf = tpl % {"name": confdata["name"], "asterisk": str_srv, "extension": str_ext, "password": str_pw}
  #dst = open(os.path.join(dstpath, CONF), "w")
  #dst.write(conf)

  #os.makedirs(asterdstpath, exist_ok = True)
  #tpl = open(os.path.join(srcpath, ASTERCONF)).read()


  x[0].conf["address"] = confdata["manager_host"]
  x[0].conf["port"] = confdata["manager_port"]
  x[0].conf["username"] = confdata["manager_user"]
  x[0].conf["secret"] = confdata["manager_pw"]
  x[0].conf["internalcontext"] = "from-internal"
  x[0].conf["ext"] = str_ext
  x[0].conf["pw"] = str_pw
  x[0].conf["query_str"] = q_url
  x[0].conf["do_not_ask"] = int_dna

  x[0].set(1)
  root.quit()

def ask_config(conf):
  root = Tk()

  Label(root, text="Сервер").grid(row=1,column=1)
  Label(root, text="Номер").grid(row=2,column=1)
  Label(root, text="Пароль").grid(row=3,column=1)
  Label(root, text="Не запрашивать").grid(row=4,column=1)

  srv_var = StringVar(value = conf.get("address", ""))
  srv = Entry(root, textvariable = srv_var)
  #srv.insert(END)
  srv.grid(row=1, column=2)
  srv.focus()

  ext_var = StringVar(value = conf.get("ext", ""))
  ext = Entry(root, textvariable = ext_var)
  #ext.insert(END)
  ext.grid(row=2, column=2)

  pw_var = StringVar(value = conf.get("pw", ""))
  pw = Entry(root, textvariable = pw_var)
  #pw.insert(END)
  pw.grid(row=3, column=2)

  dna_var = IntVar(value = conf.get("do_not_ask", 0))
  dna = Checkbutton(root, variable=dna_var)
  dna.grid(row=4, column=2)

  saved = IntVar(value = 0)
  saved.conf = conf
  Button(root, command = lambda x = root, y = [saved, srv_var, ext_var, pw_var, dna_var]: save(x, y), text="Сохранить").grid(row=100, column=1, columnspan=2, sticky=W+E)
  root.mainloop()
  root.quit()
  print(saved.get())
  return saved.conf

TPL_microsip_ini="""[Settings]
accountId=1
enableLocalAccount=0
crashReport=1
enableLog=0
randomAnswerBox=0
portKnockerHost=
portKnockerPorts=
updatesInterval=never
checkUpdatesTime=1502302706
DTMFMethod=0
autoAnswer=2
denyIncoming=
usersDirectory=
STUN=
enableSTUN=0
singleMode=1
silent=0
localDTMF=1
ringingSound=
audioInputDevice=""
audioOutputDevice=""
audioRingDevice=""
audioCodecs=opus/16000/1 PCMA/8000/1 PCMU/8000/1
VAD=0
EC=0
forceCodec=0
videoCaptureDevice=""
videoCodec=
disableH264=0
bitrateH264=256
disableH263=0
bitrateH263=256
disableVP8=0
bitrateVP8=256
mainX=965
mainY=383
mainW=315
mainH=377
noResize=0
messagesX=415
messagesY=383
messagesW=0
messagesH=0
ringinX=0
ringinY=0
callsWidth0=0
callsWidth1=0
callsWidth2=0
callsWidth3=0
callsWidth4=0
contactsWidth0=0
volumeOutput=100
volumeInput=100
activeTab=0
alwaysOnTop=0
autoHangUpTime=0
maxConcurrentCalls=1
cmdCallStart=
cmdCallEnd=
cmdIncomingCall=
cmdCallAnswer=
[Account1]
label=%(name)s
server=%(asterisk)s
proxy=
domain=%(asterisk)s
username=%(extension)s
password=%(password)s
authID=
displayName=
voicemailNumber=
transport=tls
publicAddr=
SRTP=
publish=0
ICE=0
allowRewrite=1
disableSessionTimer=0
[Calls]
[Dialed]
"""


if __name__ == "__main__":
  print(ask_config({"address": "test"}))

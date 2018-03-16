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
  x[0].conf["port"] = int(confdata["manager_port"])
  x[0].conf["username"] = confdata["manager_user"]
  x[0].conf["secret"] = confdata["manager_pw"]
  x[0].conf["internalcontext"] = "from-internal"
  x[0].conf["ext"] = str_ext
  x[0].conf["pw"] = str_pw
  x[0].conf["query_str"] = q_url
  x[0].conf["do_not_ask"] = int_dna

  x[0].set(1)
  root.destroy()

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

# sip-communicator.properties
TPL_jitsi="""#Sample config with one XMPP and one SIP account configured
# Replace {sip-pass-hash} with SIP user password hash
# as well as other account properties

# Name of default JVB room that will be joined if no special header is included
# in SIP invite
org.jitsi.jigasi.DEFAULT_JVB_ROOM_NAME=siptest

net.java.sip.communicator.impl.protocol.SingleCallInProgressPolicy.enabled=false

# Should be enabled when using translator mode
#net.java.sip.communicator.impl.neomedia.audioSystem.audiosilence.captureDevice_list=["AudioSilenceCaptureDevice:noTransferData"]

# Adjust opus encoder complexity
net.java.sip.communicator.impl.neomedia.codec.audio.opus.encoder.COMPLEXITY=10

# Disables packet logging
net.java.sip.communicator.packetlogging.PACKET_LOGGING_ENABLED=true

net.java.sip.communicator.impl.protocol.sip.acc1403273890647=acc1403273890647
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.ACCOUNT_UID=SIP\:<<JIGASI_SIPUSER>>
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.PASSWORD=<<JIGASI_SIPPWD>>
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.PROTOCOL_NAME=SIP
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.SERVER_ADDRESS=<<JIGASI_SIPSERVER>>
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.USER_ID=<<JIGASI_SIPUSER>>
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.KEEP_ALIVE_INTERVAL=25
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.KEEP_ALIVE_METHOD=OPTIONS
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.VOICEMAIL_ENABLED=false
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.AMR-WB/16000=750
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.G722/8000=700
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.GSM/8000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.H263-1998/90000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.H264/90000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.PCMA/8000=600
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.PCMU/8000=650
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.SILK/12000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.SILK/16000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.SILK/24000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.SILK/8000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.VP8/90000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.iLBC/8000=10
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.opus/48000=1000
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.red/90000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.speex/16000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.speex/32000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.speex/8000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.telephone-event/8000=1
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.Encodings.ulpfec/90000=0
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.OVERRIDE_ENCODINGS=true

# Used when incoming calls are used in multidomain environment, used to detect subdomains
# used for constructing callResource and eventually contacting jicofo
net.java.sip.communicator.impl.protocol.sip.acc1403273890647.DOMAIN_BASE=<<DOMAIN_BASE>>

# the pattern to be used as bosh url when using bosh in multidomain environment
#net.java.sip.communicator.impl.protocol.sip.acc1403273890647.BOSH_URL_PATTERN=https://{host}{subdomain}/http-bind?room={roomName}

# can be enabled to disable audio mixing and use translator, jigasi will act as jvb, just forward every ssrc stream it receives.
#net.java.sip.communicator.impl.protocol.sip.acc1403273890647.USE_TRANSLATOR_IN_CONFERENCE=true

# We can use the prefix org.jitsi.jigasi.xmpp.acc to override any of the
# properties that will be used for creating xmpp account for communication.

# The following two props assume we are using jigasi on the same machine as
# the xmpp server.
org.jitsi.jigasi.xmpp.acc.IS_SERVER_OVERRIDDEN=true
org.jitsi.jigasi.xmpp.acc.SERVER_ADDRESS=127.0.0.1
org.jitsi.jigasi.xmpp.acc.VIDEO_CALLING_DISABLED=true
# Or you can use bosh for the connection establishment by specifing the URL to use.
# org.jitsi.jigasi.xmpp.acc.BOSH_URL_PATTERN=https://server.com/http-bind?room={roomName}

#Used when outgoing calls are used in multidomain environment, used to detect subdomains
#org.jitsi.jigasi.xmpp.acc.DOMAIN_BASE=<<DOMAIN_BASE>>
#org.jitsi.jigasi.xmpp.acc.BOSH_URL_PATTERN=https://{host}{subdomain}/http-bind?room={roomName}

# can be enabled to disable audio mixing and use translator, jigasi will act as jvb, just forward every ssrc stream it receives.
#org.jitsi.jigasi.xmpp.acc.USE_TRANSLATOR_IN_CONFERENCE=true

# If you want jigasi to perform authenticated login instead of anonymous login
# to the XMPP server, you can set the following properties.
# org.jitsi.jigasi.xmpp.acc.USER_ID=SOME_USER@SOME_DOMAIN
# org.jitsi.jigasi.xmpp.acc.PASS=SOME_PASS
# org.jitsi.jigasi.xmpp.acc.ANONYMOUS_AUTH=false

# If you want to use the SIP user part of the incoming/outgoing call SIP URI
# you can set the following property to true.
# org.jitsi.jigasi.USE_SIP_USER_AS_XMPP_RESOURCE=true

# Activate this property if you are using self-signed certificates or other
# type of non-trusted certicates. In this mode your service trust in the 
# remote certificates always.
# net.java.sip.communicator.service.gui.ALWAYS_TRUST_MODE_ENABLED=true

# Enable this property to be able to shutdown gracefully jigasi using
# a rest command
# org.jitsi.jigasi.ENABLE_REST_SHUTDOWN=true

# Options regarding Transcription. Read the README for a detailed description
# about each property

# delivering final transcript
# org.jitsi.jigasi.transcription.DIRECTORY=/var/lib/jigasi/transcripts
# org.jitsi.jigasi.transcription.BASE_URL=http://localhost/
# org.jitsi.jigasi.transcription.PORT=-1
# org.jitsi.jigasi.transcription.ADVERTISE_URL=false

# save formats
# org.jitsi.jigasi.transcription.SAVE_JSON=false
# org.jitsi.jigasi.transcription.SAVE_TXT=true

# send formats
# org.jitsi.jigasi.transcription.SEND_JSON=true
# org.jitsi.jigasi.transcription.SEND_TXT=false
"""

if __name__ == "__main__":
  print(ask_config({"address": "test"}))

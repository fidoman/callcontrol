import os

def list_clients():
  avail = []
  for c, func in conf_functions.items():
    if func(None, checkonly=True):
      avail.append(c)
  return avail

def configure_client(client_name, asterisk_conf):
  conf_functions[client_name](asterisk_conf)
  # choose methot depending by os in conf_function

def make_microsip_conf(c, x):
  global TPL_microsip_ini
  with open(x, "w") as conffile:
    conffile.write(TPL_microsip_ini%c)
  os.system("taskkill /f /im MicroSIP.exe")

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
label=%(address)s
server=%(address)s
proxy=
domain=%(address)s
username=%(ext)s
password=%(pw)s
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


def make_jitsi_conf(c):
#use props.hsql.script.default file (it must be saved just after jitsi install)
  addition = [
    ('net.java.sip.communicator.plugin.provisioning.METHOD', 'Manual'),
#    ('net.java.sip.communicator.plugin.provisioning.URL', c["data"]+'?what=jitsiconf&user=${username}&password=${password}&os=${osname}&hw=${hwaddr}&uuid=${uuid}&hostname=${hostname}')
    ('net.java.sip.communicator.plugin.provisioning.URL', '%(data)s?what=jitsiconf&ext=%(ext)s&pw=%(pw)s'%c)
  ]
#server must reply with properties file from template below

  if os.name == "nt":
    confpath = os.path.expandvars(r"%APPDATA%\Jitsi")
  else:
    confpath = os.path.expandvars(r"$HOME/.jitsi")

  default_conf = os.path.join(confpath, "props.hsql.script.default")
  actual_conf = os.path.join(confpath, "props.hsql.script")
  if not os.path.exists(default_conf):
    import shutil
    shutil.copy(actual_conf, default_conf)


  default = open(default_conf).read()
  actual = open(actual_conf, "w")
  if default[-1]!="\n":
    default += "\n"
  actual.write(default)

  for a in addition:
    actual.write("INSERT INTO PROPS VALUES('%s','%s')\n"%a)

  actual.close()

#  global TPL_jitsi
#  with open(x, "w") as conffile:
#    conffile.write(TPL_jitsi%c)

# sip-communicator.properties
TPL_jitsi="""net.java.sip.communicator.impl.gui.accounts.acc1522053277238.accountIndex = 0
net.java.sip.communicator.impl.gui.accounts.acc1522053277238.lastAccountStatus = Online
net.java.sip.communicator.impl.gui.accounts.acc1522053277238 = SIP:%(ext)s@%(address)s
net.java.sip.communicator.impl.gui.accounts.acc1522053277238.wizard = net_java_sip_communicator_plugin_sipaccregwizz_SIPAccountRegistrationWizard
net.java.sip.communicator.impl.gui.minimizeInsteadOfHide = true

net.java.sip.communicator.impl.protocol.SingleCallInProgressPolicy.enabled=true

service.gui.AUTO_POPUP_NEW_MESSAGE = yes

net.java.sip.communicator.impl.protocol.sip.acc1522053275550 = acc1522053275550
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ACCOUNT_UID = SIP:%(ext)s@%(address)s
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SERVER_ADDRESS = %(address)s
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SERVER_PORT = 5060
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.AUTO_ANSWER_CONDITIONAL_NAME = Answer-Mode
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.AUTO_ANSWER_CONDITIONAL_VALUE = Auto
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.AUTO_ANSWER_WITH_VIDEO = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PASSWORD = %(pw)s
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PROTOCOL_NAME = SIP
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PROXY_ADDRESS = %(address)s
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PROXY_AUTO_CONFIG = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PROXY_PORT = 5061
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.USER_ID = %(ext)s@%(address)s
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SUBSCRIPTION_EXPIRATION = 3600

net.java.sip.communicator.impl.protocol.sip.acc1522053275550.AMR-WB/16000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.DEFAULT_ENCRYPTION = true
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.DEFAULT_SIPZRTP_ATTRIBUTE = true
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.DTMF_METHOD = AUTO_DTMF
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.DTMF_MINIMAL_TONE_DURATION = 70
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.AMR-WB/16000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.G722/8000 = 705
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.G723/8000 = 150
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.GSM/8000 = 450
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.H264/90000 = 1100
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.iLBC/8000 = 500
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.opus/48000 = 750
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.PCMA/8000 = 600
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.PCMU/8000 = 650
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.red/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.rtx/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.SILK/12000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.SILK/16000 = 713
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.SILK/24000 = 714
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.SILK/8000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.speex/16000 = 700
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.speex/32000 = 701
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.speex/8000 = 352
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.telephone-event/8000 = 1
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.ulpfec/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.VP8/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.Encodings.VP9/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL.DTLS-SRTP = 2
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL.SDES = 1
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL_STATUS.DTLS-SRTP = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL_STATUS.SDES = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL_STATUS.ZRTP = true
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ENCRYPTION_PROTOCOL.ZRTP = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.FORCE_P2P_MODE = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.FORCE_PROXY_BYPASS = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.G722/8000 = 705
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.G723/8000 = 150
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.GSM/8000 = 450
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.H264/90000 = 1100
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.iLBC/8000 = 500
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.IS_PRESENCE_ENABLED = true
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.KEEP_ALIVE_INTERVAL = 25
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.KEEP_ALIVE_METHOD = OPTIONS
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.OPT_CLIST_SERVER_URI =
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.OPT_CLIST_USER =
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.OPT_CLIST_USE_SIP_CREDETIALS = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.opus/48000 = 750
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.OVERRIDE_ENCODINGS = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PCMA/8000 = 600
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PCMU/8000 = 650
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.POLLING_PERIOD = 30
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.PREFERRED_TRANSPORT = TLS
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.red/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.rtx/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SAVP_OPTION = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SDES_CIPHER_SUITES = AES_CM_128_HMAC_SHA1_80,AES_CM_128_HMAC_SHA1_32
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SILK/12000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SILK/16000 = 713
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SILK/24000 = 714
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.SILK/8000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.speex/16000 = 700
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.speex/32000 = 701
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.speex/8000 = 352
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.telephone-event/8000 = 1
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.ulpfec/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.VOICEMAIL_CHECK_URI =
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.VOICEMAIL_ENABLED = true
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.VOICEMAIL_URI =
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.VP8/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.VP9/90000 = 0
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.XCAP_ENABLE = false
net.java.sip.communicator.impl.protocol.sip.acc1522053275550.XIVO_ENABLE = false
"""




# configurator functions
#  subfunction to check possibility to configure
#  subfunction to really configure

def conf_microsip(c, checkonly=False):
  if os.name != "nt":
    if checkonly:
      return False
    raise Exception("MicroSIP is supported in Windows only")

  if checkonly:
    return True
  make_microsip_conf(c, os.path.expandvars(r"%APPDATA%\MicroSIP\microsip.ini"))

def conf_jitsi(c, checkonly=False):
  if checkonly:
    return True
  if os.name == "nt":
    make_jitsi_conf(c) #, os.path.expandvars(r"%APPDATA%\Jitsi\sip-communicator.properties"))
  else:
    make_jitsi_conf(c) #, os.path.expandvars(r"$HOME/.jitsi/sip-communicator.properties"))


conf_functions = {
  "microsip": conf_microsip, 
  "jitsi": conf_jitsi
}

if __name__=="__main__":
  print("available configurators:", list_clients())

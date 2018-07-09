# asterisk activity monitor
#  - users online time
#  - users queue active time
#  - users call/speak time
# events relay for subscribed extensions:
#  - extension status
#  - external channel status watching for calls came to the extension
#    notifications about call that gone to other extension/parked/returned

# 1) connect to asterisk AMI
# 2) accept connection from operator software
#    minimum delay on requests

# collect messages for online extensions
# drop if count more than
MAX_MESSAGES=1000

# queues for extensions
# queues for calls
# subscriptions for extensions
# subscriptions for calls
# each message must be copied to all subscriptions
# queue for each subscription
# 1) put message
# 2) enable semaphore

import time
from asterisk.ami import *

from config import asterisk_conf


def event_listener(event,**kwargs):
  print("event:", event)



client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
client.add_event_listener(event_listener)

def asterisk_reconnect(cl, resp):
  global client
  #global client, asterisk_conf, my_extension
  # reinit exts
  # may give invalid state ifstill not fully booted
  print("RECONNECT")
  #print(resp)
#  cl.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
#  print("logged in")
#  cl.add_event_listener(event_listener)
#  print("readded listener")
  #time.sleep(5) # allow asterisk to bring up on restart
  #init_extension(client, asterisk_conf["internalcontext"], my_extension.get())

def disc(cl, resp):
  print("lost connection")

#keeper = AutoReconnect(client, on_reconnect=asterisk_reconnect, on_disconnect=disc, delay=2)
#keeper.finished = threading.Event()
#client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])


#while keeper.finished is None:
#  print("keeper is not initialized")
#  time.sleep(1)

#print("keeper is initialized")

#try:
#  while True:
#    time.sleep(1)
#    print(keeper._login_args)
#except:
#  print('exc')

#keeper.finished.set()

# must test: 
#  1) reconnect if connection is timed out
#  2) reconnect if asterisk is restarted
#  3) check if asterisk is fully booted

def servicer_thread():
  # communication with client
  pass

def listener_thread():
  # accept client connection and start dialog
  pass

def resp(x):
  print("resp", x)

need_login = True

while True:
  try:
    if need_login:
      client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
      need_login = False
    print(client.send_action(SimpleAction('Ping'), callback=resp))
  except Exception as e:
    print(e)
    need_login = True
    client.disconnect()

  time.sleep(1)

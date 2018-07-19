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
import time
import socket

from asterisk.ami import *

from config import asterisk_conf


def event_listener(event,**kwargs):
  print("event:", event)


client = None

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

# QUEUES
#  - put on command queue command and reference of output queue to put result with id assigned to command
#  - restart command loop if ping command timed out

# loop: wait for queue/time out
# if command, send it and put reply onto output queue
# if timed out, send Ping
# if loop not returned (hang in AMI module), restart it


def resp(x):
  print("callback")
  print("error?", x.is_error())
  print("keys",x.keys)
  print("status", x.status)
  print("---")

need_login = True
first_login = True

command_semaphore = threading.Semaphore(value=0) # signals when command arrives
command_lock = threading.Lock() # command queue access
command_queue = [] # insert(0, cmd) to put, .pop() to fetch

while True:
  try:
    if need_login:
      print("logging on")
      client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
      client.add_event_listener(event_listener)
      r=client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])

      #print("login:", r.response)
      need_login = False
    # fetch command
    acq = command_semaphore.acquire(timeout=5)
    if acq: # acquired something
      print("execute command")
      with command_lock:
        cmd, label, outq = command_queue.pop()
        # command; label for marking reply; output queue
        print(cmd)
    else:
      print("command timeout")
      print(client.send_action(SimpleAction('Ping'), callback=resp).response)
      print(client._futures)
  except Exception as e:
    print("Exception:", e)
    need_login = True
    try:
      client.disconnect()
      del client
    except:
      pass
    print("disconnected")
    continue

  try:
    if len(client._futures) > 3:
      print("client hang")
      need_login = True
      client.disconnect()
      del client
  except:
    pass



  time.sleep(0.2)

# client listener:
#  accept connection
#  authenticate
#  subscribe for events

# on connect:
#   client send's its extension number. all other messages are encrypted with extension's password
# incoming messages:
#   dial external number, callerid
#   park
#   return parknumber
#   returnto parknumber, extension
#   hangup
#   atxfer extension
#   blindxfer extension
#   extensions -- resend all extensions statuses
# outgoing messages
#   client's extension event
#   call event -- subscribe since the call connects client's extension
#   extensions statuses


def client_listener():
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind((socket.gethostname(), 5010))
  serversocket.listen(5)

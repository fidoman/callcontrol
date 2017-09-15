from tkinter import *

""" Мониторинг каналов 
1. С помощью Status получить список каналов
2. Мониторить изменения каналов
"""

import time

from asterisk.ami import *
from config import asterisk_conf

def event_listener(event, source):
  #print(event, source)
  chan = event.keys.get("Channel")
  if chan:
    print(chan, event.name)

root = Tk()

client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])

def asterisk_reconnect(cl, resp):
  global client, asterisk_conf, my_extension
  print("RECONNECT", cl)
  time.sleep(5) # allow asterisk to bring up on restart

#keeper = AutoReconnect(client, on_reconnect=asterisk_reconnect, delay=5)

client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
print(client)
print(client.add_event_listener(event_listener))

#input()

action = SimpleAction(
    'Status',
)
print(client.send_action(action, callback=print).get_response())
#print("run")

root.mainloop()

#try: 
#  while True:
#    time.sleep(1)
#finally:

#  keeper.finished.set()

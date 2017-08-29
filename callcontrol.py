from tkinter import *
import time
import threading
import os
import json
import traceback
from datetime import datetime

from statuswindow import status_window_operation

from config import asterisk_conf, call_log_dir, load_data

from persistqueue import Queue
call_log = Queue(call_log_dir)


root = Tk()
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
window_w, window_h = 320, 200
space_h, space_v = 32, 40
margin_h, margin_v = 64, 4
#pos_x, pos_y = screen_w - space_h - window_w, screen_h - space_v - window_h

call_windows = [] # list of notification windows
# add at end, remove as user closes

# Основное окно
#  ввод экстеншна
#  для теста - кнопка "создать окошко"
# При обнаружении звонка - окно Toplevel
#  добавлять в верх стека. Убирать те, где оператор нажал "Закрыть".



def list_commands():
  global client
  action = SimpleAction(
    'ListCommands',
  )
  client.send_action(action, callback=print)
  #client.logoff()



root.title("test window")
my_extension = StringVar()

ext_label = Label(root, text="Внутренний номер")
ext_label.grid(row=1, column=1)
ext_entry = Entry(root, textvariable=my_extension)
ext_entry.grid(row=1, column=2)

add_window_button = Button(root, text="Тест", command = lambda: add_call_window("Тест", "123", "45", "x"))
add_window_button.grid(row=2, column=1)

add_window_button = Button(root, text="list", command = list_commands)
add_window_button.grid(row=2, column=2)

quit_button = Button(root, text="Выход", command=root.destroy)
quit_button.grid(row=3)
#root.mainloop(); print(my_extension.get()); exit()




def calculate_position(window_number): # from zero
  global window_w, window_h, space_h, space_v
  global screen_w, screen_h
  global margin_h, margin_v
  # spacing before each window
  max_windows_vertically = int((screen_h-margin_v)/(window_h+space_v))
  wincolumn_number = int(window_number/max_windows_vertically)
  window_number%=max_windows_vertically
  print("window #", window_number,"of", max_windows_vertically)
  downside = screen_h-space_v-window_number*(window_h+space_v)-margin_v
  rightside = screen_w-space_h-margin_h-wincolumn_number*(window_w+space_h)
  return rightside-window_w, downside-window_h

def transfer_window(ch):
  print("transferring", ch)
  t = Toplevel()
  t.title("transfer "+ch)
  status_window_operation("transfer", t, ch)



def add_call_window(callerid, shop_info, operator, channel):
 try:
  global call_windows
  global shops
  global call_tags
  cw = Toplevel()
  cw.wm_attributes('-topmost', 1)
  cw.title("%s->%s [%s] %s"%(callerid, shop_info[0], operator, channel))

  cw.ring_time = None
  cw.answer_time = None
  cw.end_time = None
  cw.operator = operator # save for logging
  cw.shopphone = shop_info[2]

  sv_label = Label(cw, text="Состояние")
  statusvar = StringVar()
  sv_data = Label(cw, textvariable = statusvar)
  sv_label.grid(row=0,column=0)
  sv_data.grid(row=0,column=1)
  transf_b = Button(cw, text='Переключить', command=lambda ch=channel: transfer_window(ch))
  transf_b.grid(row=0,column=3)

  cw.client = StringVar(value=callerid)

  k = Label(cw, text='Клиент:')
  k.grid(row=1, column=0)
  k = Entry(cw, textvariable=cw.client)
  k.grid(row=1, column=1)

  cw.shopname = StringVar(value=shop_info[0])

  k = Label(cw, text='Магазин:')
  k.grid(row=2, column=0)
  k = Label(cw, textvariable=cw.shopname)
  k.grid(row=2, column=1)

  cw.tag = StringVar()

  k = Label(cw, text="Тэг")
  k.grid(row=4,column=0)
  k = OptionMenu(cw, cw.tag, *call_tags)
  k.grid(row=4,column=1, columnspan=3, sticky=W)


  k = Label(cw, text="Комментарий")
  k.grid(row=5,column=0)
  cw.note = Text(cw, height=3, width=24)
  cw.note.grid(row=5,column=1, columnspan=3)

  close_btn = Button(cw, text="Завершено", command = lambda: close_call_window(cw))
  close_btn.grid(row=6,column=0)
  cw.protocol("WM_DELETE_WINDOW", lambda: close_call_window(cw))

  x, y = calculate_position(len(call_windows))
  cw.geometry('%dx%d+%d+%d'%(window_w, window_h, x, y))
  call_windows.append(cw)

  return cw, statusvar
 except:
  traceback.print_exc()
  return None, None


def open_shop_doc(shop_info):
  page = shop_info[1]
  if page:
    print("Open", page)
    os.system('start '+page)
  else:
    print("no script page")
#    os.system('start https://google.com')


def close_call_window(window):
  global call_windows, call_log
  if not window.tag.get():
    return False
  print("CLOSE", window.tag.get(), window.rec_uid)
  call_log.put({
	"tag": window.tag.get(), 
	"operator": window.operator,
	"rec_uid": window.rec_uid, 
	"client_phone": window.client.get(),
        "shop_phone": window.shopphone,
        "shop_name": window.shopname.get(),
        "ring_time": window.ring_time,
        "answer_time": window.answer_time,
        "end_time": window.end_time,
        "note": window.note.get(1.0, END),
        "close_time": datetime.utcnow()
  })

  #print(id(window))
  pos = 0
  for w in call_windows:
    if id(w)==id(window):
      break
    pos+=1
  else:
    print("window not found")
    return

  window.destroy()
  call_windows.pop(pos)
  while pos<len(call_windows):
    x, y = calculate_position(pos)
    try:
      call_windows[pos].geometry('+%d+%d'%(x, y))
    except:
      print("window", pos, "is lost")
    pos+=1

#print(pos_x, pos_y)
#root.geometry('%dx%d-%d-%d'%(window_w, window_h, space_h, space_v))


#show_window = lambda: root.deiconify(); root.lift(); root.wm_attributes('-topmost', 1)
#hide_window = lambda: root.wm_withdraw()

import urllib.parse
import urllib.request

def bg_task():
  # connect to asterisk and wait for incoming data
  global bg_run, asterisk_conf, root, show_window, call_log
  note_empty = False
  print("start bg_task")
  while bg_run:
    time.sleep(2)
    if call_log.qsize():
      note_empty = True
      z = call_log.get()
      try:
        print(repr(urllib.parse.urlencode(z)))
        cmd_params = urllib.parse.urlencode({'what': 'log_call', 'ext': asterisk_conf["ext"], 'pw': asterisk_conf["pw"]})
        data_params = urllib.parse.urlencode(z)
        url = asterisk_conf["data"] + "?" + cmd_params + "&" + data_params
        resp = urllib.request.urlopen(url)
        if resp.headers.get_content_type() != 'application/json':
          print("error:", repr(resp.read(1000)))
          call_log.put(z)
          raise Exception("server did not return JSON data")
        else:
          print(resp.read(1000))

      except Exception as e:
        print(e)
        print("queue drop", repr(z))

      call_log.task_done()

    else:
      if note_empty:
        print("queue is empty")
        note_empty = False

#    root.iconify()
#    root.wm_withdraw()
#    time.sleep(1)
#    show_window()

# *** connecting asterisk ***

from asterisk.ami import *

client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])

def unsip(n):
  # remove sip prefix and normalize number
  _,n = n.split("/",1)
#  print("unsip", repr(n))
  if len(n)==11 and n[0]=="7":
    n="+"+n
  return n

calls = {}
myext = set((asterisk_conf["ext"],))
state = []

#logf = open("events3.log", "w")
logf = None

def event_listener(event,**kwargs):
  try:
    global calls, myext, state
    global show_window, hide_window
    global shops
    if event.name!="Registry" and event.name!="PeerStatus":
      print(event.name)
    if logf:
      logf.write("--- " + repr(event.name) + "\n")
      logf.write("  " + str(event.keys) + "\n")
      #logf.write(".. " + repr(calls)+"\n\n")

    if event.name=="Newchannel":
      print("\\", event.keys) #["Uniqueid"])
      calls[event.keys["Uniqueid"]] = {}
      calls[event.keys["Uniqueid"]]["callerid"] = event.keys["CallerIDNum"]
      calls[event.keys["Uniqueid"]]["destination"] = event.keys["Exten"]
      calls[event.keys["Uniqueid"]]["channel"] = event.keys["Channel"]

    if event.name=="Rename":
      print("\\", event.keys) #["Uniqueid"])
      calls[event.keys["Uniqueid"]]["channel"] = event.keys["Newname"]


    elif event.name=="Dial":
      dial = event.keys.get("Dialstring")
      callerchan = event.keys.get("UniqueID") # get info for calling line here
      calledchan = event.keys.get("DestUniqueID") # attach window here
      chan = event.keys.get("Channel")
      dest = event.keys.get("Destination")
      subevt = event.keys.get("SubEvent")
      print(f"\\ {subevt} {dial}: {chan} [{callerchan}] -> {dest} [{calledchan}]")
      print("++", event.keys)
      print("caller:", calls.get(callerchan))
      print("callee:", calls.get(calledchan))
      if subevt=="Begin":
        calls[callerchan]["calleduid"] = calledchan
        # classify call:
        #   from external to operator
        #   to external
        #   other

        if chan.startswith("SIP/sipout"):
          print("call from sipout")
          shop_sipout_ext = calls[callerchan]["destination"]
          int_ext = dial
          channel_of_interest = callerchan
          external = calls[callerchan]["callerid"]
        elif dial.startswith("sipout"):
          print("call to sipout")
          channel_of_interest = calledchan
          int_ext = calls[callerchan]["destination"]
          external = dial.split("/",1)[1]
          # requre that all sipout channel are named as sipoutNNN
          shop_sipout_ext = dial.split("/",1)[0][len("sipout"):]
        else:
          print("other call")
          channel_of_interest = None
          int_ext = None
          shop_sipout_ext = None
          external = None

        print(f"External {external} on {channel_of_interest} internal {int_ext} shop {shop_sipout_ext}")

#        lbr = calls[callerchan].get("localbridge")
 #       print("call to", dial, "local bridge to %s"%lbr if lbr else '')
#        if lbr:
 #         print("bridged:", calls[lbr])
  #        lbrcalleduid=calls[lbr].get("calleduid")
#          callee = calls.get(lbrcalleduid)
#          print("  callee:", callee)
#          if callee: 
#            sv = callee.get("statusvar")
#            if sv:
#              sv.set("Dial")
#            sw = callee.get("window")
#            if sw:
#              callee_n = unsip(dial)
#              sw.client.set(callee_n)
#              sw.rec_uid = callerchan

        # bridged call: use ConnectedLineNum
        # else: use callerchan's destination
#        if lbr:
#          shop_phone = event.keys.get("ConnectedLineNum")
#          print("Shop phone=", shop_phone)
#          shop_info = shops.by_phone.get(shop_phone, ["Нет данных", ""])
#        else:

        #shop_ext = calls[callerchan].get("destination", "")
#        print("Shop ext=", shop_sipout_ext)

        if int_ext in myext:
#          if len(calls[callerchan].get("callerid", "")) == 3:
#            print("internal call from", calls[callerchan].get("callerid", ""))
#          elif event.keys["Channel"].startswith("Local"):
#            print("local call")
#          else:
            print("Create status window on channel", channel_of_interest)
            shop_info = shops.by_dest.get(shop_sipout_ext, ["Нет данных x1", "x2", "x3"])
            cw, sv = add_call_window(external, 
					shop_info,
					dial, channel_of_interest)
            calls[channel_of_interest]["window"] = cw
            cw.shop_info = shop_info

            if (calls[callerchan] or {}).get("monitored"):
              cw.rec_uid = callerchan
              print("recording is on calling channel")
            elif (calls[calledchan] or {}).get("monitored"):
              cw.rec_uid = calledchan
              print("recording is on called channel")
            else:
              print("recording is not enabled")
              cw.rec_uid = None

            calls[channel_of_interest]["statusvar"] = sv
            cw.ring_time = datetime.utcnow()

            calls[callerchan]["calleduid"] = calledchan
            sv.set("Ringing")

    elif event.name=="Newstate":
      print("\\", event.keys.get("Uniqueid"), event.keys.get("ChannelState"))
      #print(event.keys)
      if event.keys.get("ChannelState")=='6': # ANSWER
        uid=event.keys.get("Uniqueid")
        print("call", uid, "is Up", calls[uid])
        sv=calls[uid].get("statusvar")
        if sv:
          sv.set("Up")
        sw=calls[uid].get("window")
        if sw:
          sw.answer_time = datetime.utcnow()
          open_shop_doc(sw.shop_info)

    elif event.name=="Hangup":
      uid = event.keys["Uniqueid"]
      print("\\", uid)
      c = calls.pop(uid)
      #print(event.keys)
      cw = c.get("window")
      if cw:
        cw.end_time = datetime.utcnow()
      sv = c.get("statusvar")
      if sv:
        sv.set("Ended")
      lbr = c.get("localbridge")
      if lbr:
        print("unbridge", lbr)
        calls[lbr].pop("localbridge")
        # or may be delete from list?

    elif event.name=="Shutdown":
      print("shutdown")
      state.append("shutdown")

    elif event.name=="Masquerade":
        print(event.keys)

    elif event.name=="MonitorStart":
#        print(event.keys)
        uid = event.keys["Uniqueid"]
        c=calls.get(uid)
        c["monitored"] = True
        print(f"Recording start on channel {uid}")
        sw = c.get("window")
        if sw:
          print(f"rec_uid={uid} same as window")
          sw.rec_uid = uid

    elif event.name=="MonitorStop":
        uid = event.keys["Uniqueid"]
        print(f"Recording stop on channel {uid}")
        c=calls.get(uid)
        if c:
          c["monitored"] = False


    elif event.name=="LocalBridge":
      uid1 = event.keys["Uniqueid1"]
      uid2 = event.keys["Uniqueid2"]
      print("\\  %s<->%s"%(uid1, uid2))
      calls[uid1]["localbridge"] = uid2
      calls[uid2]["localbridge"] = uid1
      # may be we need lists here?

    elif event.name=="Bridge":
      uid1 = event.keys["Uniqueid1"]
      uid2 = event.keys["Uniqueid2"]
      bstate = event.keys["Bridgestate"]
      print(f"\\  {bstate} {uid1}<->{uid2}")
#      calls[uid1]["localbridge"] = uid2
#      calls[uid2]["localbridge"] = uid1
      # may be we need lists here?


  except:
    traceback.print_exc()


client.add_event_listener(event_listener)

# ***************************

class ShopsData:
  def __init__(self):
    global asterisk_conf
    self.by_phone = {}
    self.by_dest = {}

  def load(self):
    for s in load_data("shops"):
      #print(s) 
      self.by_phone[s[1]] = self.by_dest[s[3]] = (s[0], s[2], s[1])
      # name, script, phone


shops = ShopsData()
shops.load()
#print(shops.by_dest); exit()

call_tags = []
for tag_id, tag_name in load_data("tags"):
  call_tags.append(tag_name)

#print(call_tags)
#print(dir(root))
#print(root.winfo_screenwidth(), root.winfo_screenheight())

bgthread = threading.Thread(target=bg_task)
bg_run = True
bgthread.start()

#root.wm_withdraw()
root.mainloop()
#time.sleep(10)

#root.destroy()
bg_run = False
root.quit()

bgthread.join()


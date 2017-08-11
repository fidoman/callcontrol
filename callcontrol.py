from tkinter import *
import time
import threading
import os
import json
import traceback
import urllib.request

from statuswindow import status_window_operation

from config import asterisk_conf

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
  k = Text(cw, height=3, width=24)
  k.grid(row=5,column=1, columnspan=3)

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

def update_call_window(cw, dial):
  print("*",dial)
  cw.shopname.set(dial)
  print("***",dial)

def open_shop_doc(shop_info):
  page = shop_info[1]
  if page:
    print("Open", page)
    os.system('start '+page)
  else:
    print("no script page")
#    os.system('start https://google.com')


def close_call_window(window):
  global call_windows
  if not window.tag.get():
    return False
  print("CLOSE", window.tag.get(), window.rec_uid)

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

def bg_task(root):
  # connect to asterisk and wait for incoming data
  global show_window
  while True:
    time.sleep(2)
#    root.iconify()
    root.wm_withdraw()
    time.sleep(1)
    show_window()

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

def event_listener(event,**kwargs):
  try:
    global calls, myext, state
    global show_window, hide_window
    global shops
    if event.name!="Registry" and event.name!="PeerStatus":
      print(event.name)
#    print("---", repr(event.name), event.keys, calls)

    if event.name=="Newchannel":
      print("\\", event.keys) #["Uniqueid"])
      calls[event.keys["Uniqueid"]] = {}
      calls[event.keys["Uniqueid"]]["callerid"] = event.keys["CallerIDNum"]
      calls[event.keys["Uniqueid"]]["destination"] = event.keys["Exten"]
      calls[event.keys["Uniqueid"]]["channel"] = event.keys["Channel"]

    elif event.name=="Dial":
      dial = event.keys.get("Dialstring")
      callerchan = event.keys.get("UniqueID") # get info for calling line here
      calledchan = event.keys.get("DestUniqueID") # attach window here
      subevt = event.keys.get("SubEvent")
      print("\\", subevt, dial, "[%s->%s]"%(callerchan, calledchan))
      if subevt=="Begin":
        calls[callerchan]["calleduid"] = calledchan
        lbr = calls[callerchan].get("localbridge")
        print("call to", dial, "local bridge to %s"%lbr if lbr else '')
        if lbr:
          print("bridged:", calls[lbr])
          lbrcalleduid=calls[lbr].get("calleduid")
          callee = calls.get(lbrcalleduid)
          print("  callee:", callee)
          if callee: 
            sv = callee.get("statusvar")
            if sv:
              sv.set("Dial")
            sw = callee.get("window")
            if sw:
              callee_n = unsip(dial)
              sw.client.set(callee_n)
              sw.rec_uid = callerchan
              # update client info in window
#              update_call_window(sw, dial)

        # bridged call: use ConnectedLineNum
        # else: use callerchan's destination
        if lbr:
          shop_phone = event.keys.get("ConnectedLineNum")
          print("Shop phone=", shop_phone)
          shop_info = shops.by_phone.get(shop_phone, ["Нет данных", ""])
        else:
          shop_ext = calls[callerchan].get("destination", "")
          print("Shop ext=", shop_ext)
          shop_info = shops.by_dest.get(shop_ext, ["Нет данных", ""])

        if dial in myext:
          print("Create status window on channel", calledchan)
          cw, sv = add_call_window("+"+calls[callerchan].get("callerid", ""), 
					shop_info,
					dial, calls[callerchan]["channel"])
          calls[calledchan]["window"] = cw
          cw.shop_info = shop_info
          cw.rec_uid = callerchan
          calls[calledchan]["statusvar"] = sv
          calls[calledchan]["calleruid"] = callerchan
          sv.set("Ringing")

    elif event.name=="Newstate":
      print("\\", event.keys.get("Uniqueid"), event.keys.get("ChannelState"))
      if event.keys.get("ChannelState")=='6':
        #print(event.keys)
        uid=event.keys.get("Uniqueid")
        print("call", uid, "is Up", calls[uid])
        sv=calls[uid].get("statusvar")
        sw=calls[uid].get("window")
        if sv:
          sv.set("Up")
          try:
            calleruid = calls[uid]["calleruid"]
            print("caller:", calleruid)
            if sw:
              open_shop_doc(sw.shop_info)
          except:
            print("could not open script page")
          #ch=event.keys.get("Channel")
          #print("up:", ch, uid, calls[uid])
          #calls[uid]["channel"] = ch

    elif event.name=="Hangup":
      uid = event.keys["Uniqueid"]
      print("\\", uid)
      c = calls.pop(uid)
      #print(event.keys)
      cw = c.get("window")
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

    elif event.name=="Bridge":
        print(event.keys)

    elif event.name=="Rename":
        print(event.keys)

    elif event.name=="LocalBridge":
      uid1 = event.keys["Uniqueid1"]
      uid2 = event.keys["Uniqueid2"]
      print("\\  %s<->%s"%(uid1, uid2))
      calls[uid1]["localbridge"] = uid2
      calls[uid2]["localbridge"] = uid1
      # may be we need lists here?

  except:
    traceback.print_exc()


client.add_event_listener(event_listener)

# ***************************

class ShopsData:
  def __init__(self):
    global asterisk_conf
    self.shops_url = asterisk_conf["data"]+"?what=shops"
    self.by_phone = {}
    self.by_dest = {}

  def load(self):
    for s in json.load(urllib.request.urlopen(self.shops_url)):
      #print(s) 
      self.by_phone[s[1]] = (s[0], s[2])
      self.by_dest[s[3]] = (s[0], s[2])


shops = ShopsData()
shops.load()
#print(shops.by_dest); exit()

call_tags = []
for tag_id, tag_name in json.load(urllib.request.urlopen(asterisk_conf["data"]+"?what=tags")):
  call_tags.append(tag_name)

print(call_tags)

#print(dir(root))

#print(root.winfo_screenwidth(), root.winfo_screenheight())

#bgthread = threading.Thread(target = lambda: bg_task(root))
#bgthread.start()

#root.wm_withdraw()
root.mainloop()
#time.sleep(10)

#root.destroy()
root.quit()


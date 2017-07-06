from tkinter import *
import time
import threading
import os
import json
import traceback

from statuswindow import status_window_operation

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
  client.logoff()



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



def add_call_window(callerid, destination, operator, channel):
 try:
  global call_windows
  global shops
  global call_tags
  cw = Toplevel()
  cw.wm_attributes('-topmost', 1)
  cw.title("%s->%s [%s] %s"%(callerid, destination, operator, channel))

  sv_label = Label(cw, text="Состояние")
  statusvar = StringVar()
  sv_data = Label(cw, textvariable = statusvar)
  sv_label.grid(row=0,column=0)
  sv_data.grid(row=0,column=1)
  transf_b = Button(cw, text='Переключить', command=lambda ch=channel: transfer_window(ch))
  transf_b.grid(row=0,column=3)

  k = Label(cw, text='Магазин:')
  k.grid(row=1, column=0)
  k = Label(cw, text=shops.by_dest.get(destination, ["Нет данных"])[0])
  k.grid(row=1, column=1)

  k = Label(cw, text="Тэг")
  k.grid(row=2,column=0)
  k = OptionMenu(cw, StringVar(), *call_tags)
  k.grid(row=2,column=1, columnspan=3, sticky=W)

  k = Label(cw, text="Комментарий")
  k.grid(row=3,column=0)
  k = Text(cw, height=3, width=24)
  k.grid(row=3,column=1, columnspan=3)

  print("Shop:", shops.by_dest.get(destination, ["Нет данных"]))

  
  close_btn = Button(cw, text="Завершено", command = lambda: close_call_window(cw))
  close_btn.grid(row=5,column=0)
  cw.protocol("WM_DELETE_WINDOW", lambda: close_call_window(cw))

  x, y = calculate_position(len(call_windows))
  cw.geometry('%dx%d+%d+%d'%(window_w, window_h, x, y))
  call_windows.append(cw)

  for page in shops.by_dest.get(destination, [None,[]])[1]:
    print("Open", page)
    os.system('start '+page)
#  os.system('start https://google.com')

  return cw, statusvar
 except:
  traceback.print_exc()
  return None, None

def close_call_window(window):
  global call_windows
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


show_window = lambda: root.deiconify(); root.lift(); root.wm_attributes('-topmost', 1)
hide_window = lambda: root.wm_withdraw()

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

client = AMIClient(address='asterisk.fidoman.ru', port=5038)
client.login(username='fastery', secret='fast7733')

calls = {}
myext = set(("202",))
state = []

def event_listener(event,**kwargs):
  try:
    global calls, myext, state
    global show_window, hide_window
    print(event.name)
    #print(repr(event.name), calls, event.keys)

    if event.name=="Newchannel":
      print("Newchannel", event.keys) #["Uniqueid"])
      calls[event.keys["Uniqueid"]] = {}
      calls[event.keys["Uniqueid"]]["callerid"] = event.keys["CallerIDNum"]
      calls[event.keys["Uniqueid"]]["destination"] = event.keys["Exten"]
      calls[event.keys["Uniqueid"]]["channel"] = event.keys["Channel"]

    elif event.name=="Dial":
      dial = event.keys.get("Dialstring")
      callerchan = event.keys.get("UniqueID") # get info for calling line here
      calledchan = event.keys.get("DestUniqueID") # attach window here
      subevt = event.keys.get("SubEvent")
      if subevt=="Begin":
        calls[callerchan]["calleduid"] = calledchan
        print("call to", dial)
        if dial in myext:
          cw, sv = add_call_window(calls[callerchan].get("callerid", ""), 
					calls[callerchan].get("destination", ""),
					dial, calls[callerchan]["channel"])
          calls[calledchan]["window"] = cw
          calls[calledchan]["statusvar"] = sv
          calls[calledchan]["calleruid"] = callerchan
          sv.set("Ringing")

    elif event.name=="Newstate":
      if event.keys.get("ChannelState")=='6':
        #print(event.keys)
        uid=event.keys.get("Uniqueid")
        sv=calls[uid].get("statusvar")
        if sv:
          sv.set("Up")
          #ch=event.keys.get("Channel")
          #print("up:", ch, uid, calls[uid])
          #calls[uid]["channel"] = ch

    elif event.name=="Hangup":
      print("Hangup", event.keys["Uniqueid"])
      c = calls.pop(event.keys["Uniqueid"])
      #print(event.keys)
      cw = c.get("window")
      sv = c.get("statusvar")
      if sv:
        sv.set("Ended")

    elif event.name=="Shutdown":
      print("shutdown")
      state.append("shutdown")

  except:
    traceback.print_exc()


client.add_event_listener(event_listener)

# ***************************

class ShopsData:
  def __init__(self):
    self.fname = "shops.json"
    self.sipdest = 'sipdest.json'
    self.by_phone = {}
    self.by_dest = {}

  def load(self):
    for s in json.load(open(self.fname)):
      #print(s) 
      self.by_phone[s[1]] = (s[0], s[2])
    for d, ph in json.load(open(self.sipdest)):
      self.by_dest[d] = self.by_phone[ph]


shops = ShopsData()
shops.load()

call_tags = json.load(open("tags.json", encoding="utf-8"))

#print(dir(root))

#print(root.winfo_screenwidth(), root.winfo_screenheight())

#bgthread = threading.Thread(target = lambda: bg_task(root))
#bgthread.start()

#root.wm_withdraw()
root.mainloop()
#time.sleep(10)

#root.destroy()
root.quit()


#!/usr/bin/python3

# Written by Sergey Dorofeev <sergey@fidoman.ru> for Fastery
# Year 2017

from tkinter import *
import time
import threading
import os
import json
import traceback
from datetime import datetime, timezone, timedelta
import urllib.parse
import urllib.request
import re
import consolehider

import gettext
gettext.install('callcontrol')

import config
from config import asterisk_conf, call_log_dir, load_data, backend_query


from statuswindow import status_window_operation


from persistqueue import Queue
call_log = Queue(call_log_dir)

import browserwindow

import scheduler

########
def text_status(s):
# https://wiki.asterisk.org/wiki/display/AST/Asterisk+13+ManagerEvent_ExtensionStatus
  statuses = { 
	'-2': "BAD",
	'-1': "UNK",
	'0': "FREE", 
	'1': "TALK",
	'2': "BUSY", 
	'4': "OFF",
	'8': "RING", 
	'16': "HOLD",
	'17': "WORK",
	None: "---",  
  }
  return statuses.get(s, s)

SIPchan = re.compile("SIP/(\d+)-........$")

########

extstats = {}

root = Tk()
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
window_w, window_h = 320, 240
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


def root_quit(ev):
  global root
  consolehider.show()
  root.destroy()

is_paused = False

import dial

def do_dial():
  dial.dial(root)

def pause_queue_member(new_state=None):
  global pause_button, is_paused, asterisk_conf, ext_pause_text, ext_status
  if new_state is None:
    new_state = not is_paused
  action = SimpleAction(
    'QueuePause',
    Interface = 'SIP/'+asterisk_conf["ext"],
    Paused = new_state,
    Reason = 'User action'
  )
  client.send_action(action, callback=print)
  is_paused = new_state
  pause_button.config(text=_("Unpause") if is_paused else _("Pause"))
  ext_pause_text.set("||" if is_paused else "►")
  ext_status.config(fg="red" if is_paused else "black")
  #does not work
  #ext_status.config(background = "blue")
  #ext_status.config(disabledbackground = "red")

def campaigns_window():
  pass

root.title("Call Control")
#root.overrideredirect(True)
root.resizable(False, False)
my_extension = StringVar()
my_extension.set(asterisk_conf["ext"])
extstats[my_extension.get()] = StringVar()

ext_pause_text = StringVar()

ext_label = Label(root, text=_("Extension:"))
ext_label.grid(row=1, column=1)
ext_entry = Entry(root, textvariable=my_extension, width=8, state="readonly")
ext_entry.grid(row=1, column=2)
ext_status = Entry(root, textvariable=extstats[my_extension.get()], width=12, state="readonly")
ext_status.grid(row=1, column=3)
ext_pause = Entry(root, width=1, textvariable = ext_pause_text, state="readonly")
ext_pause.grid(row=1, column=4)
call_button = Button(root, text=_("Dial"), command = do_dial)
call_button.grid(row=1, column=5)
pause_button = Button(root, text=_("Pause"), command = pause_queue_member)
pause_button.grid(row=1, column=6)
# make this button blinking if there is sheduled calls that has come
campaigns_button = Button(root, text=_("Campaigns"), command = campaigns_window)
campaigns_button.grid(row=1, column=7)


#add_window_button = Button(root, text="Тест", command = lambda: add_call_window("123", "45", "x", "chan"))
#add_window_button.grid(row=2, column=1)

#add_window_button = Button(root, text="List", command = list_commands)
#add_window_button.grid(row=2, column=2)

#quit_button = Button(root, text="Выход", command=root.destroy)
#quit_button.grid(row=2, column=3)

consolehider.hide()

root.wm_attributes('-topmost', 1)
try:
  root.wm_attributes('-toolwindow', 1)
except:
  pass
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind("<Control-Shift-Q>", root_quit)
#root.bind("<Control-Shift-T>", lambda _: add_call_window("123", "45", "x", "chan"))
#root.bind("<Control-Shift-W>", lambda _: browserwindow.test_call())
root.bind("<Control-Shift-C>", lambda _: consolehider.switch())


def calculate_position(window_number): # from zero
  global window_w, window_h, space_h, space_v
  global screen_w, screen_h
  global margin_h, margin_v
  # spacing before each window
  max_windows_vertically = int((screen_h-margin_v)/(window_h+space_v))
  wincolumn_number = int(window_number/max_windows_vertically)
  window_number%=max_windows_vertically
  print("window #", window_number, "of", max_windows_vertically)
  downside = screen_h-space_v-window_number*(window_h+space_v)-margin_v
  rightside = screen_w-space_h-margin_h-wincolumn_number*(window_w+space_h)
  return rightside-window_w, downside-window_h

def transfer_window(ch):
  print("transferring", ch)
  t = Toplevel()
  t.title("transfer "+ch)
  status_window_operation("transfer", t, ch)

def hangup(channel):
  action = SimpleAction(
    'Hangup',
    Channel=channel
  )
  print("Hangup", channel)
  stat = client.send_action(action)
  print(stat)





def get_history(ph, shopphone, shopname):
    hist_data = backend_query('phone_history', {"phone": ph, "shop": shopname})
    if not hist_data:
      return [], {}, {}
    if "keymap" in hist_data:
          hist_list = []
          hist_full = {}

          km=hist_data["keymap"]
          for x in hist_data["list"]:
            tm = x[km["cl_ring_time"]]
            if tm: 
              tm = datetime.strptime(tm[:-6], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d %H:%M:%S")
#            rec= " ".join((x[km["cl_shop_name"]] or '-', x[km["cl_operator_name"]] or '?', x[km["tag_name"]] or 'no tag', tm or 'unknown'))
            rec= " ".join((tm or 'unknown', x[km["cl_direction"]] or "-", x[km["cl_operator_name"]] or '-', x[km["tag_name"]] or 'no tag'))
            hist_list.append(rec)
            hist_full[rec] = x
          return hist_list, km, hist_full

def show_history_details(evt, w):
  print("history", evt)
  if w.history_details_window:
    w.history_details_window.destroy()
    w.history_details_window = None

  if True:
    detw=Toplevel(w)
    detw.transient(w)
    x, y = w.winfo_x(), w.winfo_y()
    x-=300
    if x<0: x=0
    y-=300
    if y<0: y=0
    detw.geometry("290x250+%d+%d"%(x,y))
    w.history_details_window = detw

    for i in w.history.curselection():
      i = int(i)
      h_rec = w.history.get(i)
      h_data = w.history_data[h_rec]

      Label(detw, text="Звонок %d (%s)"%(h_data[w.history_keys["cl_id"]], _(h_data[w.history_keys["cl_direction"]])), anchor=W).pack(fill=X)
      Label(detw, text="Тэг: %s"%h_data[w.history_keys["tag_name"]], anchor=W).pack(fill=X)
      Label(detw, text="Время: %s"%h_data[w.history_keys["cl_ring_time"]].split(".")[0], anchor=W).pack(fill=X)
      Label(detw, text="Заказ: %s"%h_data[w.history_keys["cl_order"]], anchor=W).pack(fill=X)
      Label(detw, text="Оператор: %s %s"%(h_data[w.history_keys["cl_operator_ext"]] or '', h_data[w.history_keys["cl_operator_name"]]), anchor=W).pack(fill=X)
      Label(detw, text="%s"%h_data[w.history_keys["cl_note"]], anchor=W).pack(fill=BOTH)
      break



#    t = Text(detw)
#    t.pack(fill=BOTH)
 #   for i in w.history.curselection():
#      i = int(i)
#      h_rec = w.history.get(i)
#      h_data = w.history_data[h_rec]
      #print("h_rec=", h_rec, "h_data=", h_data)
# keys:
# tag_name cl_ring_time cl_close_time cl_id cl_operator_name cl_shop_phone cl_direction cl_tag cl_end_time cl_client_phone
# cl_answer_time cl_rand cl_shop_lkid cl_shop_name cl_note cl_order cl_operator cl_uid cl_rec_uid cl_tagdata

#      DUMP ALL:
#      for k, n in w.history_keys.items():
#        print(k, n, h_data[n])
#        t.insert(END, _(k)+": "+str(h_data[n])+"\n")

def set_call_window_callerid(cw, callerid):
  cw.callerid = callerid
  cw.title("%s->%s [%s] %s"%(cw.callerid, cw.shop_info[0], cw.operator, cw.channel))
  cw.client.set(callerid)
  cw.history.delete(0, END)
  hist = get_history(callerid, cw.shopphone, cw.shopname.get())
  if hist is None:
    cw.history.insert(END, _('<nothing here>'))
    cw.history_data = {}
    cw.history_keys = {}
  else:
    hist_list, km, hist_full = hist
    for history_record in hist_list:
      cw.history.insert(END, history_record)
    cw.history_data = hist_full
    cw.history_keys = km


def add_call_window(shop_info, operator, external_channel, internal_channel, uid):
# ..., external_channel, caller_channel
 try:
  global call_windows
  global shops
  global call_tags
  cw = Toplevel()
  cw.wm_attributes('-topmost', 1)

  x, y = calculate_position(len(call_windows))
  call_windows.append(cw)
  print("Positioning at:", x, y)
  cw.geometry('%dx%d+%d+%d'%(window_w, window_h, x, y))

  cw.direction = None
  cw.uid = uid
  cw.shop_info = shop_info
  cw.channel = external_channel
  cw.operator = operator # save for logging
  cw.callerid = None

#  cw.help_window=None -- nope - use external browser

  cw.ring_time = None
  cw.answer_time = None
  cw.end_time = None
  cw.shopphone = shop_info[1]

  cw.sticky = False # cannot close without tag
  cw.rec_uid = None # voice record

  sv_label = Label(cw, text=_("line state"))
  cw.statusvar = StringVar()
  sv_data = Label(cw, textvariable = cw.statusvar)
  sv_label.grid(row=0,column=0)
  sv_data.grid(row=0,column=1)

  hangup_b = Button(cw, text=_('hangup'), command=lambda ch=internal_channel: hangup(ch))
  hangup_b.grid(row=0,column=2)

  transf_b = Button(cw, text=_('transfer'), command=lambda ch=internal_channel: transfer_window(ch))
  transf_b.grid(row=0,column=3)

  cw.client = StringVar(value='')

  k = Label(cw, text=_('client:'))
  k.grid(row=1, column=0)
  k = Entry(cw, textvariable=cw.client, width=16)
  k.grid(row=1, column=1)

  cw.order = StringVar()

  k = Label(cw, text=_('order no:'))
  k.grid(row=1, column=2)
  k = Entry(cw, textvariable=cw.order, width=10)
  k.grid(row=1, column=3)

#  k = Button(cw, text='Создать', command=lambda: call_window_new_order(cw))
#  k.grid(row=2, column=2)
#  k = Button(cw, text='Обновить', command=lambda: call_window_refresh_orders(cw))
#  k.grid(row=2, column=3)

  cw.shopname = StringVar(value=shop_info[0])

  k = Label(cw, text=_('shop:'))
  k.grid(row=2, column=0)
  k = Label(cw, textvariable=cw.shopname)
  k.grid(row=2, column=1)

  cw.tag = StringVar()

  k = Label(cw, text=_("tag"))
  k.grid(row=4,column=0)
  k = OptionMenu(cw, cw.tag, *call_tags)
  k.grid(row=4,column=1, columnspan=3, sticky=W)


  k = Label(cw, text=_("remark"))
  k.grid(row=5,column=0)
  cw.note = Text(cw, height=3, width=24)
  cw.note.grid(row=5,column=1, columnspan=3)

  close_btn = Button(cw, text=_("finished"), command = lambda: close_call_window(cw))
  close_btn.grid(row=6,column=0)
  cw.protocol("WM_DELETE_WINDOW", lambda: close_call_window(cw))

  hframe = Frame(cw)
  hscroll = Scrollbar(hframe, orient = VERTICAL)
  cw.history = history = Listbox(hframe, yscrollcommand = hscroll.set, exportselection = 0, height=3)
  hscroll.config(command=history.yview)
  hscroll.pack(side=RIGHT, fill=Y)
  history.pack(side=LEFT, fill=BOTH, expand=1)

  history.bind("<Double-Button-1>", lambda x, parent=cw: show_history_details(x, parent))
  cw.history_details_window = None

  hframe.grid(row=7, column=0, columnspan=4, sticky=W+E)

  print("Positioning retry at:", x, y)
  cw.geometry('%dx%d+%d+%d'%(window_w, window_h, x, y))

  return cw
 except:
  traceback.print_exc()
  return None, None


def open_shop_doc(w, shop_info):
  global bg_run_showpage
  page = shop_info[2]
  if page:
    print("Open", page)
    #os.system('start '+page)
#    try:
#      w.help_window=browserwindow.show_help(page)
    bg_run_showpage = page
#    except:
#      print("error on show_help")
  else:
    print("no script page")
#    os.system('start https://google.com')


def close_call_window(window, close_unanswered = False):
  global call_windows, call_log

  if close_unanswered:

    print("withdrawing window for unanswered call...")

    if window.tag.get():
      print("no, tag is set")
      return

    if window.sticky:
      print("no, window is now sticky")
      return
  
  else:

    if window.statusvar.get()!="Ended":
      print("cannot close, call in progress")
      return

    if not window.tag.get():
      print("cannot close without tag")
      return

    print("CLOSE CALL", window.tag.get(), window.rec_uid)

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
        "close_time": datetime.utcnow(),
        "order": window.order.get(),
	"uid": window.uid,
        "direction": window.direction,
        "shop_lkid": window.shop_info[5]
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

#  if window.help_window:
#    try:
#      window.help_window.close()
#    except:
#      print("error on help_window.close()")


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

def call_window_new_order(e):
  args = {"operator": e.operator, "client": e.client.get(), "shop": e.shopname.get()}
  d = backend_query("new_order", args)
  print(args, d)
  if d is None:
    return
  e.order.set(d["order_id"])
  os.system("start "+d["order_url"])
  #return d
  # start browser window

def call_window_refresh_orders(e):
  # get list of orders of current client and populate menu
  args = {"operator": e.operator, "client": e.client.get(), "shop": e.shopname.get()}
  d = backend_query("list_orders", {"operator": e.operator, "client": e.client.get(), "shop": e.shopname})
  print(e, d)

def show_window(x):
  print("show")
  root.deiconify(); root.lift() #; root.wm_attributes('-topmost', 1)

def hide_window(x):
  print("hide")
  root.wm_withdraw()

#hide_window(0)

#root.bind("<Control-Shift-H>", hide_window)
#root.bind("<Control-Shift-V>", show_window)


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
          raise Exception("server did not return JSON data")
        else:
          r = json.loads(resp.read().decode("ascii"))
          print("result:", r)
          if r.get("status")!="added":
            raise Exception("record is not added on server")

      except Exception as e:
        call_log.put(z)
        print("put back, error:", e)

      call_log.task_done()

    else:
      if note_empty:
        print("queue is empty")
        note_empty = False

# *** connecting asterisk ***

from asterisk.ami import *

client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])

def asterisk_reconnect(cl, resp):
  global client, asterisk_conf, my_extension
  # reinit exts
  # may give invalid state ifstill not fully booted
  print("RECONNECT", cl)
  time.sleep(5) # allow asterisk to bring up on restart
  init_extension(client, asterisk_conf["internalcontext"], my_extension.get())

keeper = AutoReconnect(client, on_reconnect=asterisk_reconnect, delay=5)
#keeper.finished = threading.Event()

#keeper

client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])


def unsip(n):
  """ remove sip prefix and normalize number """
  n = n.split("/",1)[-1]
#  print("unsip", repr(n))
  if len(n)==11 and n[0]=="7":
    n="+"+n
  return n

calls = {}
myext = set((asterisk_conf["ext"],))
state = []
bridges = {} # asterisk 13 BridgeUniqueid -> [member]

#logf = open("events3.log", "w")
logf = None

def event_listener(event,**kwargs):
  try:
    global calls, myext, state
    global show_window, hide_window
    global shops
    global extstats
    if event.name!="Registry" and event.name!="PeerStatus" and event.name!="QueueMemberStatus":
      print(event.name)
    if logf:
      logf.write("--- " + repr(event.name) + "\n")
      logf.write("  " + str(event.keys) + "\n")
      #logf.write(".. " + repr(calls)+"\n\n")

    if event.name=="Newchannel":
      print("\\", event.keys) #["Uniqueid"])
      uid = event.keys["Uniqueid"]
      calls[uid] = {
        "callerid": event.keys["CallerIDNum"],
        "destination": event.keys["Exten"],
        "channel": event.keys["Channel"],
        "state": event.keys["ChannelState"],
        "statedesc": event.keys["ChannelStateDesc"],
        "context": event.keys["Context"]
      }

    if event.name=="Rename":
      print("\\", event.keys) #["Uniqueid"])
      calls[event.keys["Uniqueid"]]["channel"] = event.keys["Newname"]


    elif event.name=="Dial" or event.name=="DialBegin":
      print(event.keys)
      dial = event.keys.get("Dialstring") or event.keys.get("DialString")
      callerchan = event.keys.get("UniqueID") or event.keys.get("Uniqueid") # get info for calling line here
      calledchan = event.keys.get("DestUniqueID") or event.keys.get("DestUniqueid") # attach window here
      chan = event.keys.get("Channel")
      dest = event.keys.get("Destination") or event.keys.get("DestChannel")
      subevt = event.keys.get("SubEvent")
#      print(f"\\ {subevt} {dial}: {chan} [{callerchan}] -> {dest} [{calledchan}]")
      print("\\ "+str(subevt)+" "+str(dial)+": "+str(chan)+" ["+str(callerchan)+"] -> "+str(dest)+" ["+str(calledchan)+"]")
      print("caller:", callerchan, calls.get(callerchan))
      print("callee:", calledchan, calls.get(calledchan))
      if subevt=="Begin" or event.name=="DialBegin":
       if callerchan:
        calls[callerchan]["calleduid"] = calledchan
        # classify call:
        #   from external to operator
        #   to external
        #   other

        make_sticky = False
        direction = None
        if chan.startswith("SIP/sipout"):
          print("call from sipout")
          shop_sipout_ext = calls[callerchan]["destination"]
          int_ext = dial
          external_channel = callerchan
          internal_channel = calledchan

          # use known callerid or try to get it from current message
          external = calls[callerchan]["callerid"]
          if external == "<unknown>":
            external = event.keys.get("CallerIDNum") # after transfer newstate does not contain callerid
            calls[callerchan]["callerid"] = external

          direction = "incoming"
        elif dial.startswith("sipout"):
          print("call to sipout")
          external_channel = calledchan
          internal_channel = callerchan
          int_ext = calls[callerchan]["destination"]
          external = dial.split("/",1)[1]
          # requre that all sipout channel are named as sipoutNNN
          shop_sipout_ext = dial.split("/",1)[0][len("sipout"):]
          make_sticky = True
          direction = "outgoing"
        else:
          print("other call")
          external_channel = None
          internal_channel = None
          int_ext = None
          shop_sipout_ext = None
          external = None

        print("External "+str(external)+" on "+str(external_channel)+" internal "+str(int_ext)+" shop "+str(shop_sipout_ext)+"; "+str(callerchan)+"-->"+str(calledchan)+"")

        lbr = calls[callerchan].get("localbridge")
        lbrcalleduid = None
        if lbr:
          lbrcalleduid=calls[lbr].get("calleduid")
          print("call to "+str(dial)+" local bridge to "+str(lbr)+"/"+str(lbrcalleduid)+"")
#          lbrcallee = calls.get(lbrcalleduid)
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

        try:
          int_ext = unsip(int_ext) # for DialBegin with extension as 'SIP/NNN'
        except:
          pass

        if int_ext in myext:
#          if len(calls[callerchan].get("callerid", "")) == 3:
#            print("internal call from", calls[callerchan].get("callerid", ""))
#          elif event.keys["Channel"].startswith("Local"):
#            print("local call")
#          else:
            print("Dial: create call window on channel uid", external_channel)
            if "window" in calls[external_channel]:
              print("window exists, rewriting phone: "+str(external)+" new uid "+str(callerchan)+"")
              cw = calls[external_channel]["window"]
              set_call_window_callerid(cw, unsip(external))
              cw.uid = cw.uid or callerchan 
            else:
              shop_info = shops.by_dest.get(shop_sipout_ext, ["Нет данных x1", "", "x3", "x4","x5","x6"])
              cw = add_call_window(shop_info, int_ext, external_channel, internal_channel, callerchan) #lbrcalleduid or callerchan) it is easy on asterisk 13
              cw.direction = direction
              set_call_window_callerid(cw, unsip(external))
              print("new window "+str(cw.direction)+" uid "+str(cw.uid)+" phone "+str(unsip(external))+"")
              calls[external_channel]["window"] = cw
              cw.statusvar.set(calls[external_channel]["statedesc"])

            if make_sticky:
              cw.sticky = True
              # open shop script instantly on operator-initiated calls
            #open help instantly, it must be rady before call is taken
            open_shop_doc(cw, cw.shop_info)

            if (calls[callerchan] or {}).get("monitored"):
              cw.rec_uid = callerchan
              print("recording is on calling channel")
            elif (calls[calledchan] or {}).get("monitored"):
              cw.rec_uid = calledchan
              print("recording is on called channel")
            else:
              print("recording is not enabled")
              cw.rec_uid = None

            cw.ring_time = datetime.utcnow()

            #calls[callerchan]["calleduid"] = calledchan
       else:
          print("call without caller channel")

    elif event.name=="Newstate":
      cstate = event.keys.get("ChannelState")
      cstatedesc = event.keys.get("ChannelStateDesc")
      chan = event.keys.get("Channel")
      cnum = event.keys.get("ConnectedLineNum")
      cname = event.keys.get("ConnectedLineName")
      uid=event.keys.get("Uniqueid")

      chaninfo = calls.setdefault(uid, {})
      print("\\ "+str(uid)+" "+str(chan)+" "+str(chaninfo.get('state'))+" ("+str(chaninfo.get('statedesc'))+") -> "+str(cstate)+" ("+str(cstatedesc)+") == "+str(cnum)+" "+str(cname)+"")
      chaninfo["state"] = cstate
      chaninfo["statedesc"] = cstatedesc

      # first, create call window
      # second, update status in new window or already existing
      if cstate=='5': # RING
        context = chaninfo.get("context")
        sip_ext = None
        if context == asterisk_conf["internalcontext"]:
          sip_ext_m = SIPchan.match(chan)
          if sip_ext_m:
            sip_ext = sip_ext_m.group(1)
            print("Extension="+str(sip_ext)+" caller_name="+str(cname)+"")
#            if cname:
#              print("need call window")
#              if "window" in chaninfo:
#                print("call window exists")
#              else:
#                print(f"Newstate: create call window on "+uid+" shop="+cname+"")
#                shop_info = shops.by_name.get(cname, ["Нет данных x1", "скрипт", "x3"])
#                cw = add_call_window(shop_info, sip_ext, uid, None)
#                cw.direction = "incoming"
#                set_call_window_callerid(cw, cnum)
#                chaninfo["window"] = cw
#                cw.ring_time = datetime.utcnow()
#            else:
#              print("no caller name, cannot determine shop, skip window creation")
          else:
            print("cannot parse channel name")
        else:
          print("not internal")


      #print("newstate - get status window")
      cw=calls[uid].get("window")
      if cw:
        #print("update status to", cstatedesc)
        cw.statusvar.set(cstatedesc)
      else:
        print("newstate - no cw", cstatedesc)


      if cstate=='6': # ANSWER
        print("call", uid, "is Up", calls[uid])
        cw=calls[uid].get("window")
        if cw:
          cw.answer_time = datetime.utcnow()
          cw.sticky = True
          open_shop_doc(cw, cw.shop_info)


    elif event.name=="Hangup":
      uid = event.keys["Uniqueid"]
      print("\\", uid)
      c = calls.pop(uid)
      #print(event.keys)
      cw = c.get("window")
      if cw:
        cw.end_time = datetime.utcnow()
        cw.statusvar.set("Ended")
        close_call_window(cw, True)
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
        print(event.keys)
        uid = event.keys["Uniqueid"]
        c=calls.get(uid)
        c["monitored"] = True
        print("Recording start on channel "+str(uid)+"")
        sw = c.get("window")
        if sw:
          print("rec_uid="+str(uid)+" same as window")
          sw.rec_uid = uid

    elif event.name=="MonitorStop":
        uid = event.keys["Uniqueid"]
        print("Recording stop on channel "+str(uid)+"")
        c=calls.get(uid)
        if c:
          c["monitored"] = False


    elif event.name=="LocalBridge":
      #print(event.keys);exit()
      uid1 = event.keys.get("Uniqueid1") or event.keys.get("LocalOneUniqueid")
      uid2 = event.keys.get("Uniqueid2") or event.keys.get("LocalTwoUniqueid")
      print("\\  %s<->%s"%(uid1, uid2))
      if uid1 and uid2:
        calls[uid1]["localbridge"] = uid2
        calls[uid2]["localbridge"] = uid1
        # may be we need lists here?

    elif event.name=="BridgeCreate":
      buid = event.keys["BridgeUniqueid"]
      bridges[buid] = [{"type": event.keys["BridgeType"]}, set()] # parameters, members

    elif event.name=="BridgeDestroy":
      buid = event.keys["BridgeUniqueid"]
      del bridges[buid]

    elif event.name=="BridgeEnter":
      buid = event.keys["BridgeUniqueid"]
      uid = event.keys["Uniqueid"]
      bridges[buid][1].add(uid)

      changes = False
      if calls.get(uid, {}).get("monitored"):
        bridges[buid][0]["rec_uid"] = uid
        changes = True

      if calls.get(uid, {}).get("window"):
        bridges[buid][0]["window"] = uid
        changes = True

      if changes and "window" in bridges[buid][0] and "rec_uid" in bridges[buid][0]:
        w_chan = bridges[buid][0]["window"]
        rec_uid = bridges[buid][0]["rec_uid"]
        print("setting rec_uid for window on channel "+str(w_chan)+" to "+str(rec_uid)+"")
        calls[w_chan]["window"].rec_uid = rec_uid
        del w_chan, rec_uid

    elif event.name=="BridgeLeave":
      buid = event.keys["BridgeUniqueid"]
      uid = event.keys["Uniqueid"]
      bridges[buid][1].remove(uid)
#      print(event.keys)


    elif event.name=="Bridge":
      uid1 = event.keys["Uniqueid1"]
      uid2 = event.keys["Uniqueid2"]
      bstate = event.keys["Bridgestate"]
      print("\\  "+str(bstate)+" "+str(uid1)+"<->"+str(uid2)+"")

      if calls.get(uid1, {}).get("monitored") and calls.get(uid2, {}).get("window"):
        calls[uid2]["window"].rec_uid = uid1
        print("windows on "+str(uid2)+" has monitor on "+str(uid1)+"")

      if calls.get(uid2, {}).get("monitored") and calls.get(uid1, {}).get("window"):
        calls[uid1]["window"].rec_uid = uid2
        print("windows on "+str(uid1)+" has monitor on "+str(uid2)+"")
      # may be we need lists here?

      if calls.get(uid2, {}).get("window"):
        calls[uid2]["window"].uid = calls[uid2]["window"].uid or uid1

      if calls.get(uid1, {}).get("window"):
        calls[uid1]["window"].uid = calls[uid1]["window"].uid or uid2


    elif event.name=="ExtensionStatus": # Exten Context Hint Status
      print(event.keys)
      if event.keys["Exten"] not in extstats:
        extstats[event.keys["Exten"]] = StringVar()
      v = extstats[event.keys["Exten"]]
      v.set(text_status(event.keys["Status"]))
      print(event.keys["Exten"], "->", v.get())

    elif event.name=="Join":
      print(event.keys)

    elif event.name=="Leave":
      print(event.keys)

#    elif event.name=="QueueMemberStatus":
#      print(event.keys)

    elif event.name=="QueueCallerAbandon":
      print(event.keys)


  except:
    traceback.print_exc()

def init_extension(client, context, e):
  global extstats

  action = SimpleAction(
    'ExtensionState',
    Exten=e,
    Context=context
  )
  stat = client.send_action(action)
  #print(stat.response.keys)

  if e not in extstats:
    extstats[e] = StringVar()
  v = extstats[e]
  v.set(text_status(stat.response.keys["Status"]))
  print(e, "=>", v.get())
  return v


client.add_event_listener(event_listener)
init_extension(client, asterisk_conf["internalcontext"], my_extension.get())


# ***************************

class ShopsData:
  def __init__(self):
    global asterisk_conf
    self.by_phone = {}
    self.by_dest = {}
    self.by_name = {}

  def load(self):
    for s in load_data("shops"):
      #print(s) 
      self.by_phone[s[1]] = self.by_dest[s[3]] = self.by_name[s[0]] = s
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
bg_run_showpage = None
bgthread.start()

def init_help_window():
  global bg_run, bg_run_showpage
  try:
    browserwindow.show_help("about:blank")
    print("help window have been initialized")
    counter=0
    while bg_run:
      if bg_run_showpage:

        browserwindow.show_help(bg_run_showpage)
        bg_run_showpage = None
      if counter==25:
        browserwindow.update_help_window_conf()
        counter=0
      time.sleep(0.2)
      counter+=1
    browserwindow.close_help()
  except Exception as e:
    print(e)



bg2 = threading.Thread(target=init_help_window)
bg2.start()

scheduler.root = root

bg_sched = threading.Thread(target=scheduler.run_scheduler)
bg_sched.start()


#root.wm_withdraw()

#threading.Thread(target=lambda: pause_queue_member(True)).start() # start paused
pause_queue_member(True)
root.mainloop()
#time.sleep(10)

#root.destroy()
bg_run = False
scheduler.bg_run = False
root.quit()

keeper.finished.set()

print("waiting threads...")
bgthread.join()
#bg2.join() - can hang
bg_sched.join()

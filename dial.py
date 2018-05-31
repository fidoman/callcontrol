""" Окно выбора интернет-магазина для совершения исходящего звонка.
    Список магазинов
    Строка - название, номер.
    Ввод:
      а) телефон клиента
      б) номер заказа
    Кнопка "позвонить".

    При удачном звонке хорошо бы закрывать окно вызова

"""

import re
import json
import traceback
from tkinter import *

from order import order_window

from config import asterisk_conf, load_data

from asterisk.ami import *

""" get extension of client registered with same IP - do not work over NAT """

def initiate_call(callerid, ext, phone):
  global asterisk_conf     
  print("CALL:", callerid, ext, phone)
  client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
  client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
  action = SimpleAction('Originate',                                          
                                Channel = "Local/"+ext+"@from-internal-auto",
                                Context = 'call-out',
                                Exten = phone,
                                Priority = 1,
                                WaitTime = 15,
                                Callerid = callerid)
  print(action)
  stat = client.send_action(action)
  print(stat.response)


#srch_var = StringVar()

#shops_list = Listbox(dialw)
#shops_list.pack()

def normalize_phone(ph):
  ph=re.sub("[-() ]+", "", ph)
  if len(ph)==10:
    ph="+7"+ph
  elif ph.startswith("810"):
    ph="+"+ph[3:]
  elif ph.startswith("8"):
    ph="+7"+ph[1:]
  elif ph.startswith("7") and len(ph)==11:
    ph="+"+ph

  return ph[1:]

def fix_rus(event):
  print(event)
  if event.char=="\x16" and event.keysym!='v':
    print("paste")
    event.widget.event_generate("<<Paste>>")
    print("ok")


def filter_shops(filter_str, shop_frames):
  for fr, name, row, ph in shop_frames:
    if name.lower().find(filter_str.lower())!=-1 or ph.find(filter_str)!=-1:
      fr.grid(row=row)
    else:
      fr.grid_forget()

#def place_shops(w, shops, filter_str):
#  row=1
#  for s in shops:
#    show = s[0].startswith(filter_str)
#    shop_label = Label(shops_frame, text=s[0])
#    if show:
#      shop_label.grid(row=row, column=1)
#    else:
#      shop_
#    shop_phone = Label(shops_frame, text=normalize_phone(s[1]))
#    shop_phone.grid(row=row, column=2)
#    row+=1

def srch_upd(newval, idx, action, shop_frames):
#  global shops_list, shops
  try:
#    shops_list.delete(0, END)
#    for s in shops:
#      sname=s[0]
#      if sname.lower().startswith(newval.lower()):
#        shops_list.insert(END, sname)
    filter_shops(newval, shop_frames)
  except:
    traceback.print_exc()
  return True #if len(newval)<=3 else False


def dial_old(root):
  if root is None:
    dialw = Tk()
  else:
    dialw = Toplevel(root)

  shop_frames = []

  srch_entry = Entry(dialw, validate="key", validatecommand=(dialw.register(lambda x, y, z, t=shop_frames: srch_upd(x, y, z ,t)),'%P','%i','%d'))
  srch_entry.pack()

  # add list of ...
  #   my shops and their orders
  #   list of scheduled calls

  shops = load_data("shops")
  shops_frame = Frame(dialw)
  shops_frame.pack()

  row=1
  for s in shops:
    #print(s[0], s[4])
    if s[4]!="Да":
      continue
    fr = Frame(shops_frame)
    shop_label = Label(fr, text=s[0], width=36)
    shop_label.pack(side=LEFT, fill=X, expand=True)
    ph = normalize_phone(s[1]) or 'Общий'
    shop_phone = Button(fr, text=ph, width=15, command=lambda s=s[0], ph=ph, eid=s[5]: order_window(s, ph, eid))
    shop_phone.pack(side=LEFT)
    fr.grid(column=0, row=row, sticky=W)
    shop_frames.append((fr, s[0], row, ph))
    row+=1

  srch_entry.focus()

  if not root:
    dialw.mainloop()



def update_shops_list(newval, idx, action, dialw):
  try:
    dialw.slist.delete(0, END)
    for s in dialw.shops:
      sname=s[1]+" | "+s[0]
      if sname.lower().find(newval.lower())!=-1:
        dialw.slist.insert(END, sname)
  except:
    traceback.print_exc()
  return True

def shop_click(x, t):
#  print(x.widget.get(ACTIVE))
  #print(x.widget.get(x.widget.curselection()))
  try:
    text = x.widget.get(x.widget.curselection()).split(" | ")[0]
    t.set(text)
  except:
    pass

def do_call(d, f):
  print("call", d.get(), "from", f.get())
  initiate_call(f.get(), asterisk_conf['ext'], d.get())

def load_shops():
  print("Dialw: load shops")
  shops = load_data("shops")
  shops.sort(key=lambda x: x[0].lower())
  return shops

def dial(root):
  if root is None:
    dialw = Tk()
    close_dialw = lambda w: w.destroy()
    do_create = True
  else:
    try: 
      dialw = root.dial_window
      dialw.deiconify()
      dialw.lift()
      do_create = False
    except:
      dialw = root.dial_window = Toplevel(root)
      do_create = True
    close_dialw = lambda w: w.wm_withdraw()



  if do_create:
    dialw.title("Звонок клиенту")

  # enter shop:
  # client phone:
  # after dial - connect to asterisk monitor and find initiated call. close window when call is ended
  #  is it needed?
  # close window with escape; if off-focus for 2 minutes

#    dialw.shop_var = StringVar()
    dialw.phone_var = StringVar()
    dialw.order_id = None # order to work with
    dialw.lead_id = None # call initiative identifier

    dialw.from_var = StringVar()

    sframe = Frame(dialw)
    sscroll = Scrollbar(sframe, orient = VERTICAL)
    dialw.slist = Listbox(sframe, yscrollcommand = sscroll.set, exportselection = 0)
    sscroll.config(command=dialw.slist.yview)
    sscroll.pack(side=RIGHT, fill=BOTH)
    dialw.slist.pack(side=LEFT, fill=BOTH, expand=1)

    Label(dialw, text="Клиент:").grid(row=1, column=1)
    dialw.phone_entry = Entry(dialw, textvariable=dialw.phone_var)
    dialw.phone_entry.grid(row=1, column=2)
    Label(dialw, text="Магазин:").grid(row=1, column=3)
    dialw.shop_entry = Entry(dialw, validate="key", validatecommand=(dialw.register(lambda x, y, z, t=dialw: update_shops_list(x, y, z, t)),'%P','%i','%d'))
    dialw.shop_entry.grid(row=1, column=4, sticky=W+E)

    dial_cmd = lambda d=dialw.phone_var, f=dialw.from_var: do_call(d, f)
    dial_cmd_ev = lambda _, d=dialw.phone_var, f=dialw.from_var: do_call(d, f)

    call_button = Button(dialw, textvariable=dialw.from_var, command = dial_cmd)
    call_button.grid(row=1, column=5)
    call_button.config(default = ACTIVE)

    dialw.slist.bind("<ButtonRelease-1>", lambda x, t = dialw.from_var: shop_click(x, t))
    dialw.slist.bind("<Double-Button-1>", dial_cmd_ev)

    sframe.grid(row=2, column=1, columnspan=5, sticky="NEWS")

    dialw.grid_rowconfigure(2, weight=1)
    dialw.grid_columnconfigure(4, weight=1)

    dialw.bind("<Return>", dial_cmd_ev)
    dialw.bind("<Key>", fix_rus)
    dialw.bind("<Escape>", lambda _, x=dialw: close_dialw(x))
    dialw.protocol("WM_DELETE_WINDOW", lambda x=dialw: close_dialw(x))

  # always
#  dialw.shop_var.set("")
  dialw.shop_entry.delete(0, END) # no var - use only for filtering
  dialw.phone_var.set("")
  dialw.order_id = None
  dialw.lead_id = None

  dialw.from_var.set("-----------")

  dialw.phone_entry.focus()

  dialw.shops = load_shops()
  update_shops_list(dialw.shop_entry.get(), None, None, dialw)


  if not root:
    dialw.mainloop()

if __name__ == "__main__":
  dial(None)

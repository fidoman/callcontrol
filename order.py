""" Окно создания/выбора заказа """

import json
from tkinter import *
from asterisk.ami import *

asterisk_conf = json.load(open("asterisk.json"))

""" get extension of client registered with same IP - do not work over NAT """

def initiate_call(callerid, ext, phone):
  global asterisk_conf     
  print("CALL:", callerid, ext, phone.get())
  client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
  client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
  action = SimpleAction('Originate',                                          
                                Channel = "Local/"+ext+"@from-internal",
                                Context = 'call-out',
                                Exten = phone.get(),
                                Priority = 1,
                                WaitTime = 15,
                                Callerid = callerid)
  stat = client.send_action(action)
  print(stat.response)


def order_window(shop, shop_ph):
  ow = Toplevel()
  s = Label(ow, text=shop)
  s.pack()
  call_fr = Frame(ow)
  ph_l = Label(call_fr, text="Телефон клиента:")
  ph_l.pack(side=LEFT)
  ph_entry = Entry(call_fr)
  ph_entry.pack(side=LEFT)
  call_fr.pack()   
  c = Button(ow, text="Звонок", command=lambda c=shop_ph, e='202', p=ph_entry: initiate_call(c, e, p))
  c.pack()
  ph_entry.focus()

""" Окно выбора интернет-магазина для совершения исходящего звонка.
    Список магазинов
    Строка - название, номер.
    Ввод:
      а) телефон клиента
      б) номер заказа
    Кнопка "позвонить".
"""

import re
import json
import traceback
from tkinter import *

from order import order_window

from config import asterisk_conf, load_data

shops = load_data("shops")

dialw = Tk()

def srch_upd(newval, idx, action):
#  global shops_list, shops
  try:
#    shops_list.delete(0, END)
#    for s in shops:
#      sname=s[0]
#      if sname.lower().startswith(newval.lower()):
#        shops_list.insert(END, sname)
    filter_shops(newval)
  except:
    traceback.print_exc()
  return True #if len(newval)<=3 else False

#srch_var = StringVar()
srch_entry = Entry(dialw, validate="key", validatecommand=(dialw.register(srch_upd),'%P','%i','%d'))
srch_entry.pack()

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

shops_frame = Frame(dialw)
shops_frame.pack()

shop_frames = []

row=1
for s in shops:
  fr = Frame(shops_frame)
  shop_label = Label(fr, text=s[0], width=36)
  shop_label.pack(side=LEFT, fill=X, expand=True)
  ph = normalize_phone(s[1]) or 'Общий'
  shop_phone = Button(fr, text=ph, width=15, command=lambda s=s[0], ph=ph: order_window(s, ph))
  shop_phone.pack(side=LEFT)
  fr.grid(column=0, row=row, sticky=W)
  shop_frames.append((fr, s[0], row))
  row+=1

def filter_shops(filter_str):
  global shop_frames
  for fr, name, row in shop_frames:
    if name.lower().find(filter_str.lower())!=-1:
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
srch_entry.focus()
dialw.mainloop()

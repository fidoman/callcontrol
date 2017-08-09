import os
import sys
import urllib.request
import json
from tkinter import *

dstpath = os.path.expandvars(r"%APPDATA%\MicroSIP")
srcpath = os.path.dirname(sys.argv[0])

CONF = "microsip.ini"

def save():
  global srcpath, dstpath, root, srv, ext, pw, CONF
  str_srv = srv.get()
  str_ext = ext.get()
  str_pw = pw.get()
  if not str_srv or not str_ext or not str_pw:
    root.bell()
    return

  q_url=f"https://{str_srv}/cgi-bin/data.py"

  # urlencode ext and pw
  conf = json.load(urllib.request.urlopen(f"{q_url}?what=config?ext={}&pw={}"))
  print(conf)
  # get manager user/pass from server
  return

  os.makedirs(dstpath, exist_ok = True)
  tpl = open(os.path.join(srcpath, CONF)).read()
  conf = tpl % {"extension": str_ext, "password": str_pw}
  dst = open(os.path.join(dstpath, CONF), "w")
  dst.write(conf)
  root.quit()

root = Tk()

Label(root, text="Сервер").grid(row=1,column=1)
Label(root, text="Номер").grid(row=2,column=1)
Label(root, text="Пароль").grid(row=3,column=1)

srv = Entry(root)
srv.grid(row=1, column=2)
srv.focus()
ext = Entry(root)
ext.grid(row=2, column=2)
pw = Entry(root)
pw.grid(row=3, column=2)

Button(root, command=save, text="Сохранить").grid(row=100, column=1, columnspan=2, sticky=W+E)

root.mainloop()
root.quit()

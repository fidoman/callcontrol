import os
import sys
from tkinter import *

dstpath = os.path.expandvars(r"%APPDATA%\MicroSIP")
srcpath = os.path.dirname(sys.argv[0])

CONF = "microsip.ini"

def save():
  global srcpath, dstpath, root, ext, pw, CONF
  str_ext = ext.get()
  str_pw = pw.get()
  if not str_ext or not str_pw:
    root.bell()
    return
  os.makedirs(dstpath, exist_ok = True)
  tpl = open(os.path.join(srcpath, CONF)).read()
  conf = tpl % {"extension": str_ext, "password": str_pw}
  dst = open(os.path.join(dstpath, CONF), "w")
  dst.write(conf)
  root.quit()

root = Tk()
Label(root, text="Вн.номер").grid(row=1,column=1)
Label(root, text="Пароль").grid(row=2,column=1)
ext = Entry(root)
ext.grid(row=1, column=2)
pw = Entry(root)
pw.grid(row=2, column=2)
Button(root, command=save, text="Сохранить").grid(row=3, column=1, columnspan=2, sticky=W+E)

root.mainloop()
root.quit()

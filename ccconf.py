import os
import sys
import urllib.request
import urllib.parse
import json
from tkinter import *

#dstpath = os.path.expandvars(r"%APPDATA%\MicroSIP")
#srcpath = os.path.dirname(sys.argv[0])
#CONF = "microsip.ini"

def save(root, x):
  str_srv = x[1].get()
  str_ext = x[2].get()
  str_pw = x[3].get()
  int_dna = x[4].get()
  if not str_srv or not str_ext or not str_pw:
    root.bell()
    return

  q_url="https://"+str_srv+"/cgi-bin/data.py"

  # urlencode ext and pw
  urlparams = urllib.parse.urlencode({'what': 'config', 'ext': str_ext, 'pw': str_pw})

  resp = urllib.request.urlopen(""+q_url+"?"+urlparams+"")
  if resp.headers.get_content_type() != 'application/json':
    print("error:", repr(resp.read(1000)))
    root.bell()
    return
  print(resp.headers)
  jsondata = resp.read().decode('ascii')
  print(jsondata)
  confdata = json.loads(jsondata)
  print(confdata)

  # get manager user/pass from server
  #os.makedirs(dstpath, exist_ok = True)
  #tpl = open(os.path.join(srcpath, CONF)).read()
  #conf = tpl % {"name": confdata["name"], "asterisk": str_srv, "extension": str_ext, "password": str_pw}
  #dst = open(os.path.join(dstpath, CONF), "w")
  #dst.write(conf)

  #os.makedirs(asterdstpath, exist_ok = True)
  #tpl = open(os.path.join(srcpath, ASTERCONF)).read()


  x[0].conf["address"] = confdata["manager_host"]
  x[0].conf["port"] = int(confdata["manager_port"])
  x[0].conf["username"] = confdata["manager_user"]
  x[0].conf["secret"] = confdata["manager_pw"]
  x[0].conf["internalcontext"] = "from-internal"
  x[0].conf["ext"] = str_ext
  x[0].conf["pw"] = str_pw
  x[0].conf["query_str"] = q_url
  x[0].conf["do_not_ask"] = int_dna

  x[0].set(1)
  root.destroy()

def ask_config(conf):
  root = Tk()

  Label(root, text="Сервер").grid(row=1,column=1)
  Label(root, text="Номер").grid(row=2,column=1)
  Label(root, text="Пароль").grid(row=3,column=1)
  Label(root, text="Не запрашивать").grid(row=4,column=1)

  srv_var = StringVar(value = conf.get("address", ""))
  srv = Entry(root, textvariable = srv_var)
  #srv.insert(END)
  srv.grid(row=1, column=2)
  srv.focus()

  ext_var = StringVar(value = conf.get("ext", ""))
  ext = Entry(root, textvariable = ext_var)
  #ext.insert(END)
  ext.grid(row=2, column=2)

  pw_var = StringVar(value = conf.get("pw", ""))
  pw = Entry(root, textvariable = pw_var)
  #pw.insert(END)
  pw.grid(row=3, column=2)

  dna_var = IntVar(value = conf.get("do_not_ask", 0))
  dna = Checkbutton(root, variable=dna_var)
  dna.grid(row=4, column=2)

  saved = IntVar(value = 0)
  saved.conf = conf
  Button(root, command = lambda x = root, y = [saved, srv_var, ext_var, pw_var, dna_var]: save(x, y), text="Сохранить").grid(row=100, column=1, columnspan=2, sticky=W+E)
  root.mainloop()
  print(saved.get())
  return saved.get(), saved.conf


if __name__ == "__main__":
  print(ask_config({"address": "test"}))

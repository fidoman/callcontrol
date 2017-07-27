import time
import json
from tkinter import *
from asterisk.ami import *
import traceback

asterisk_conf = json.load(open("asterisk.json"))

def text_status(s):
  statuses = { '0': "FREE", '2': "BUSY", '8': "RING", None: "UNKN", '-1': "OFF" }
  return statuses.get(s, s)


def init_extension(extstats, client, context, e):
  action = SimpleAction(
    'ExtensionState',
    Exten=e,
    Context=context
  )
  stat = client.send_action(action)
  print(stat.response.keys)

  if e not in extstats:
    extstats[e] = StringVar()
  v = extstats[e]
  v.set(text_status(stat.response.keys["Status"]))
  print(e, "->", repr(v))
  return v

def create_status_window(sw, extstats, operators, commands):
  """ sw: Tk parent
      extstat: externally updatable extension statuses
      operators: groups: operators 
      commands: name, function, args 
      """
#  sw = Toplevel()

  global asterisk_conf
  client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
  client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])

  for grp in operators.keys():
    grp_pos, grp_elements = operators[grp]
    grp_fr = Frame(sw, height=2, bd=1, relief=SUNKEN) # frame of group
    for element in grp_elements.items():
      op_txt, op_pos = element
      elem_fr = Frame(grp_fr, bd=4)  # frame for each extension with number and command buttons
      elem_lab = Label(elem_fr, text=str(op_txt))
      elem_lab.pack(side=LEFT)
      elem_stat = Label(elem_fr, textvariable=init_extension(extstats, client, asterisk_conf["internalcontext"], op_txt), width=4)
      elem_stat.pack(side=LEFT)
      for c_txt, c_func, c_arg in commands:
        cmd = lambda z=op_txt, t=c_arg: c_func(z, t)
        print(c_func, op_txt, cmd)
        c_but = Button(elem_fr, text=c_txt, command=cmd)
        c_but.pack(side=LEFT)

      elem_fr.grid(row=op_pos[0], column=op_pos[1])

    grp_fr.grid(row=grp_pos[0], column=grp_pos[1])

  client.logoff()

ops = {
   200: ( (1, 1),
        {'101': (1, 1), '102': (1, 2), '103': (2, 1) } ),
   201: ( (1, 2),
        {'104': (1, 1), '105': (2, 1), '106': (2, 2) } ),
   202: ( (2, 2),
        {'200': (1, 1), '201': (1, 2), '202': (2, 1), '203': (2, 2)} ),
   203: ( (2, 1),
        {'190': (1, 1), '191': (1, 2), '192': (2, 1), '193': (2, 2)} ),
   204: ( (1, 3),
        {'204': (1, 1), '205': (1, 2), '206': (2, 1), '207': (2, 2)} ),
   205: ( (2, 3),
        {'208': (1, 1), '209': (1, 2), '210': (2, 1), '211': (2, 2)} ),
}


def cmd_tr(ext, arg):
  client, channel, context = arg
  print(client, channel, context, ext)
  action = SimpleAction(
    'Redirect',
    Channel = channel,
    Context = context,
    Exten = ext,
    Priority = 1
  )
  r = client.send_action(action)
  print(r.response)

#ACTION: Redirect
#Channel: SIP/x7065558529-8f54
#Context: default
#Exten: 5558530
#Priority: 1

def status_updater(extstats, event, **kwargs):
  if event.name=="ExtensionStatus": # Exten Context Hint Status
    try:
      print(repr(event.keys["Exten"]), event.keys["Status"])
      if event.keys["Exten"] not in extstats:
        extstats[event.keys["Exten"]] = StringVar()
      v = extstats[event.keys["Exten"]]
      v.set(text_status(event.keys["Status"]))
      print(event.keys["Exten"], "=>", repr(v))
    except:
      traceback.print_exc()


def close_client(root, c):
  print("log off")
  root.destroy()
  try:
    c.logoff()
  except:
    traceback.print_exc()

def hangup_closer(event, w, ch, **kwargs):
  if event.name=="Hangup":
    print("CLOSE:", w, ch)
    w.closer()

def status_window_operation(mode, root, args):
  global asterisk_conf
  client = AMIClient(address=asterisk_conf["address"], port=asterisk_conf["port"])
  client.login(username=asterisk_conf["username"], secret=asterisk_conf["secret"])
  extstats = {}
  client.add_event_listener(lambda event, s=extstats, **kwargs: status_updater(s, event, **kwargs))
  if mode=="transfer":
    # args is channel
    commands = [("TR", cmd_tr, (client, args, asterisk_conf["internalcontext"]))]
    ch = args
    client.add_event_listener(lambda event, w=root, ch=ch, **kwargs: hangup_closer(event, w, ch, **kwargs))
  elif mode=="control":
    commands = []
  else:
    commands = []

  create_status_window(root, extstats, ops, commands)
  root.closer = lambda c=client, x=root: close_client(x, c)
  root.protocol("WM_DELETE_WINDOW", root.closer)

#action = SimpleAction(
#    'ExtensionState',
#    Exten='202',
#    Context='from-internal',

#    'Status',

#    'SIPpeers',

#    'Command',
#    Command='core show hints',

#)

#stat = 	client.send_action(action)
#print(stat.response)


# 0 Idle
# 8 Ringing
# 2 Up

if __name__ == "__main__":
  root=Tk()
  status_window_operation("", root, None)
  root.mainloop()

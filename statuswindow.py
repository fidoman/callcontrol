import time
import json
from tkinter import *
from asterisk.ami import *
import traceback
import urllib.parse
import urllib.request

from config import asterisk_conf

def get_operators():
    global asterisk_conf

    cmd_params = urllib.parse.urlencode({'what': 'operators', 'ext': asterisk_conf["ext"], 'pw': asterisk_conf["pw"]})
#    data_params = urllib.parse.urlencode({"phone": ph})
    url = asterisk_conf["data"] + "?" + cmd_params #+ "&" + data_params

    try:
      resp = urllib.request.urlopen(url)
      if resp.headers.get_content_type() != 'application/json':
        print("error:", repr(resp.read(1000)))
        raise Exception("server did not return JSON data")
      else:
        data = json.loads(resp.read().decode("UTF-8"))
        if "keymap" in data:
          km=data["keymap"]
#          print(km)
          for x in data["list"]:
            yield x[km["op_name"]], x[km["op_ext"]], x[km["op_group"]], x[km["op_location"]]

    except Exception as e:
      print(e)
#      yield "error: "+str(e)
      return



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

      elem_name = Label(elem_fr, text=op_names[op_txt])
      elem_name.pack(side=LEFT)

      elem_stat = Label(elem_fr, textvariable=init_extension(extstats, client, asterisk_conf["internalcontext"], op_txt), width=4)
      elem_stat.pack(side=LEFT)

      for c_txt, c_func, c_arg in commands:
        cmd = lambda z=op_txt, t=c_arg: c_func(z, t)
        print(c_func, op_txt, cmd)
        c_but = Button(elem_fr, text=c_txt, command=cmd)
        c_but.pack(side=RIGHT)

      elem_fr.grid(row=op_pos[0], column=op_pos[1], sticky=W+E)

    grp_fr.grid(row=grp_pos[0], column=grp_pos[1])

  client.logoff()

#ops = {
#   200: ( (1, 1),
#        {'101': (1, 1), '102': (1, 2), '103': (2, 1) } ),
#   201: ( (1, 2),
#        {'104': (1, 1), '105': (2, 1), '106': (2, 2) } ),
#   202: ( (2, 2),
#        {'200': (1, 1), '201': (1, 2), '202': (2, 1), '203': (2, 2)} ),
#   203: ( (2, 1),
#        {'190': (1, 1), '191': (1, 2), '192': (2, 1), '193': (2, 2)} ),
#   204: ( (1, 3),
#        {'204': (1, 1), '205': (1, 2), '206': (2, 1), '207': (2, 2)} ),
#   205: ( (2, 3),
#        {'208': (1, 1), '209': (1, 2), '210': (2, 1), '211': (2, 2)} ),
#}


def cmd_tr(ext, arg):
  client, channel, context = arg
  print("Blind transfer", client, channel, context, ext)
  action = SimpleAction(
#    'Redirect',
    'BlindTransfer', 
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

def cmd_at(ext, arg):
  client, channel, context = arg
  print("Attended transfer", client, channel, context, ext)
  action = SimpleAction(
    'Atxfer',
    Channel = channel,
    Context = context,
    Exten = ext,
    Priority = 1
  )
  r = client.send_action(action)
  print(r.response)


def cmd_spy(ext, arg):
  global astrisk_conf
  client, channel, context = arg
  print(client, channel, context, ext)

  action = SimpleAction('Originate',                                          
                                Channel = "Local/"+asterisk_conf["ext"]+"@from-internal-auto",
                                Context = 'chanspy-app', #'chanspy-app',
                                Exten = ext,
                                Priority = 1,
                                WaitTime = 15,
                                Callerid = "spy-%s"%ext)
       
  print(action)
  r = client.send_action(action)
  print(r.response)



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
    commands = [("TR", cmd_tr, (client, args, asterisk_conf["internalcontext"])),
		("AT", cmd_at, (client, args, asterisk_conf["internalcontext"]))]
    ch = args
    client.add_event_listener(lambda event, w=root, ch=ch, **kwargs: hangup_closer(event, w, ch, **kwargs))
  elif mode=="control":
    commands = [("SPY", cmd_spy, (client, args, asterisk_conf["internalcontext"]))]
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

from pprint import pprint

if True:
  op_names = {}
  ops = {}
  for name, ext, group, location in get_operators():
    print(name, ext, group, location)
    if not location: continue
    op_names[ext] = name.split(" ")[0]
    ops.setdefault(group, ((1, int(group or '0')), {}))[1][ext] = tuple(location.split(" "))

#  pprint(ops); exit()
if __name__ == "__main__":

  root=Tk()
  status_window_operation("control", root, None)
  root.mainloop()

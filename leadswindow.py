from tkinter import *
import threading

import gettext
gettext.install('callcontrol')

import config

leads_window = None

# Lead consists of:
#   Shop ID
#   Shop name
#   Shop phone
#   Client phone
#   Order number
#   Note
#   Time when to begin dial

# For selected lead also show info known for client phone:
#   calls history
#   notes 
#   tags

# Idea: add current incoming call on top of leads list
#       attaching lead to call window
#           automatic, or manual override

def select_lead(x, leadslist, myframe):
  global leads_window
  print(x, leadslist.curselection())
  for c in myframe.winfo_children():
    c.destroy()
  selection = leadslist.curselection()[:1]
  if not selection:
    return
  else:
    selection = selection[0]
  print(selection, leadslist.get(selection), leads_window.leadsmap.get(leadslist.get(selection)))
  # lead data
  fields = leads_window.leadskeys
  data = leads_window.leadsmap.get(leadslist.get(selection))
  Button(myframe, text="call", command=exit).grid(row=0, column=0)

  Label(myframe, text="shop phone").grid(row=1, column=0)
  Label(myframe, text=data[fields["l_shop_phone"]]).grid(row=1, column=1)
  Label(myframe, text="client phone").grid(row=2, column=1)
  Label(myframe, text=data[fields["l_client_phone"]]).grid(row=2, column=1)
  print(fields)

  # history
  # client note

def hide_leads_window():
  global leads_window
  leads_window.wm_withdraw()

def show_leads_window():
  global leads_window
  leads_window.deiconify()
  leads_window.lift()


def init_leads_window(root):
  global leads_window
  if leads_window:
    return
  leads_window = Toplevel(root)
  leads_window.protocol("WM_DELETE_WINDOW", hide_leads_window)

  leads_list = LabelFrame(leads_window, text=_("campaign"))
  leads_list.pack(side=LEFT, fill=Y)

  selected_lead = LabelFrame(leads_window, text=_("lead"), width=200)
  selected_lead.pack(side=LEFT, fill=Y)

  lscroll = Scrollbar(leads_list, orient=VERTICAL)
  leads = Listbox(leads_list, yscrollcommand = lscroll.set, exportselection = 0, height=50)
  leads_window.leads = leads
  lscroll.config(command=leads.yview)
  lscroll.pack(side=RIGHT, fill=Y)
  leads.pack(side=LEFT, fill=BOTH, expand=1)
  leads.bind("<Double-Button-1>", lambda x, leadslist=leads, myframe=selected_lead: select_lead(x, leadslist, myframe))

#  leads.insert(END, "123")

def update_leads_window():
  global leads_window
  leads_window.leads.delete(0, END)
  x = config.load_data("leads")
  fields = x.get('keymap')
  if not fields:
    print("no leads data")
    return
  data = x.get('list')
  print(fields)

  leads_window.leadsmap = {}
  leads_window.leadskeys = fields
  for l1 in data:
    print(l1[fields['l_shop_phone']])
    print(l1[fields['l_client_phone']])
    lead_key="%s -> %s" % (l1[fields['l_shop_phone']], l1[fields['l_client_phone']])
    leads_window.leadsmap[lead_key] = l1
    leads_window.leads.insert(END, lead_key)
  return # is there leads to call immediately for this operator

if __name__=="__main__":
  root = Tk()
  root.title("Test leads window")

  b1 = Button(root, text="update", command=update_leads_window)
  b1.pack(side=LEFT)
  b2 = Button(root, text="show", command=show_leads_window)
  b2.pack(side=LEFT)
  b3 = Button(root, text="hide", command=hide_leads_window)
  b3.pack(side=LEFT)

  init_leads_window(root)
  root.mainloop()

#https://stackoverflow.com/questions/30018148/python-tkinter-scrollable-frame-class

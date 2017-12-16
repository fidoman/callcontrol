from tkinter import *
import threading

import gettext
gettext.install('callcontrol')

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

def select_lead(x, leadslist, myframe):
  print(x, leadslist.curselection())
  for c in myframe.winfo_children():
    c.destroy()
  selection = leadslist.curselection()[:1]
  if not selection:
    return
  else:
    selection = selection[0]
  print(selection)

def hide_leads_window():
  global leads_window
  leads_window.wm_withdraw()

def show_leads_window():
  global leads_window
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
  lscroll.config(command=leads.yview)
  lscroll.pack(side=RIGHT, fill=Y)
  leads.pack(side=LEFT, fill=BOTH, expand=1)
  leads.bind("<Double-Button-1>", lambda x, leadslist=leads, myframe=selected_lead: select_lead(x, leadslist, myframe))

  leads.insert(END, "123")

def update_leads_window():
  global leads_window
  pass
  return # is there leads to call immediately for this operator

if __name__=="__main__":
  root = Tk()
  init_leads_window(root)
  root.mainloop()

#https://stackoverflow.com/questions/30018148/python-tkinter-scrollable-frame-class

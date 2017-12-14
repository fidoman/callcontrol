from tkinter import *
import threading

leads_window = None

def init_leads_window(root):
  global leads_window
  if leads_window:
    return
  leads_window = Toplevel(root)
  pass

def update_leads_window():
  global leads_window
  pass
  return # is there leads to call immediately for this operator

if __name__=="__main__":
  root = Tk()
  init_leads_window(root)
  root.mainloop()

#https://stackoverflow.com/questions/30018148/python-tkinter-scrollable-frame-class

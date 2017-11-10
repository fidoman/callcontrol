import time
from tkinter import *

from config import *

bg_run = True
root = None

def run_scheduler():
  global bg_run
  global root
  latest_lead = None
  leads = []
  # periodically update list of scheduled calls
  # take ongoing
  # notify operator
  while bg_run:
    print("fetching new lead")
    print("check if we should call")
    print("notify operator")
    print("locking if we call")
    print("calling")
    print("release will be done by server if new tag will arrive")

    time.sleep(5)

# TODO: search stale locks

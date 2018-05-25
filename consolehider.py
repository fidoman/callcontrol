import os

if os.name == "nt":

  import win32console, win32gui
  mywindow = win32console.GetConsoleWindow()
  visible = True

  def hide():
    global visible
    visible = False
    set_visibility()

  def show():
    global visible
    visible = True
    set_visibility()

  def switch():
    global visible
    visible = not visible
    set_visibility()

  def set_visibility():
    global mywindow, visible
    if visible:
      win32gui.ShowWindow(mywindow, 8)
    else:
      win32gui.ShowWindow(mywindow, 0)

else:

  def hide():
    pass

  def show():
    pass

  def switch():
    pass

  def set_visibility():
    pass

import os

from selenium import webdriver
from config import read_help_window_conf, save_help_window_conf

test_window = None

def test_call():
  global test_window
  """ if no window - create
      if exists - save position/size and close """

  if test_window is None:
    c = read_help_window_conf()
    #print(c)
    o=webdriver.ChromeOptions()
    o.add_argument("disable-infobars");
    o.add_argument("--window-size=%(w)d,%(h)d"%c);
    o.add_argument("--window-position=%(x)d,%(y)d"%c);
    test_window=webdriver.Chrome(chrome_options=o, service_args=["--verbose"])
#    test_window.set_window_position(c["x"], c["y"])
#    test_window.set_window_size(c["w"], c["h"])


  else:
    #print(dir(test_window))
    #print(test_window.get_window_position())
    #print(test_window.get_window_size())

    pos = test_window.get_window_position()
    size = test_window.get_window_size()
    test_window.close()
    save_help_window_conf({'x': pos['x'], 'y': pos['y'], 'w': size['width'], 'h': size['height']})
    test_window = None

help_window = None
help_window_conf = None


def create_window(c):
       o=webdriver.ChromeOptions()
       o.add_argument("disable-infobars");
       o.add_argument("--window-size=%(w)d,%(h)d"%c);
       o.add_argument("--window-position=%(x)d,%(y)d"%c);
       #o.add_argument("--enable-logging");
       #o.set_headless(True)
       #o.add_argument("--homepage "+url);
       return webdriver.Chrome(chrome_options=o, service_args=["--verbose", "--log-path="+os.path.join(os.environ["TEMP"], "chromedriver.log")])
#, service_log_path = os.path.join(os.environ["TEMP"], "selenium.log"))


def show_help(url, retry=True):
   global help_window, help_window_conf
   #print("open url", url)
   if help_window:
     c = help_window_conf = read_help_window_conf()
     try:
       #print("try in existing window")
       help_window.get(url) # do it first as only .get raises exception when chrome is lost; others just time-out
       help_window.set_window_position(c["x"], c["y"])
       help_window.set_window_size(c["w"], c["h"])
       #print("done")
     except Exception as e:
       #print("error", str(e), "drop old window")
       help_window = None
       show_help(url, True)

   else:
     #print("need new window")
     pass

#  if help_window:
#    print("already open", help_window.title)
#    return
     if retry:
       #print("create new window")
       c = help_window_conf = read_help_window_conf()
       help_window = create_window(c)
       show_help(url, False)
     else:
       #print("cannot show help")
       pass

def update_help_window_conf():
  global help_window, help_window_conf
  if help_window:
    pos = help_window.get_window_position()
    size = help_window.get_window_size()
    #print(pos, size)
    update = False
    if pos['x']!=help_window_conf['x']:
      help_window_conf['x'] = pos['x']
      update = True
    if pos['y']!=help_window_conf['y']:
      help_window_conf['y'] = pos['y']
      update = True
    if size['width']!=help_window_conf['w']:
      help_window_conf['w'] = size['width']
      update = True
    if size['height']!=help_window_conf['h']:
      help_window_conf['h'] = size['height']
      update = True

    if update:
      #print("Save help window disposition", help_window_conf)
      save_help_window_conf(help_window_conf)


#show_help("http://gmail.com/")
#print(dir(help_window))

#  return help_window

# except:
#  print("error in show_help")

def close_help():
  global help_window
  try:
    if help_window:
      help_window.close()
      help_window=None
  except:
    #print("error in close_help")
    pass

def test():
  import time
  try:
    show_help("https://www.mail.ru")
    time.sleep(2)
#    show_help("https://www.yandex.ru")
#    time.sleep(3)
#    show_help("https://www.google.com")
#    time.sleep(3)
  finally:
    pass
    close_help()

if __name__=="__main__":
#  import win32console, win32gui
#  mywindow = win32console.GetConsoleWindow()
#  win32gui.ShowWindow(mywindow, 0)
  test()
#  win32gui.ShowWindow(mywindow, 1)

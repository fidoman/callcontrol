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
    print(test_window.get_window_position())
    print(test_window.get_window_size())

    pos = test_window.get_window_position()
    size = test_window.get_window_size()
    test_window.close()
    save_help_window_conf({'x': pos['x'], 'y': pos['y'], 'w': size['width'], 'h': size['height']})
    test_window = None

help_window = None



def show_help(url, retry=True):
   global help_window
   try:
     c = read_help_window_conf()
     help_window.set_window_position(c["x"], c["y"])
     help_window.set_window_size(c["w"], c["h"])
     help_window.get(url)
   except:

#  if help_window:
#    print("already open", help_window.title)
#    return
     if retry:
       c = read_help_window_conf()
       o=webdriver.ChromeOptions()
       o.add_argument("disable-infobars");
       o.add_argument("--window-size=%(w)d,%(h)d"%c);
       o.add_argument("--window-position=%(x)d,%(y)d"%c);
  #o.add_argument("--homepage "+url);
       help_window=webdriver.Chrome(chrome_options=o)
       show_help(url, False)
     else:
       print("cannot show help")

#show_help("http://gmail.com/")
#print(dir(help_window))

#  return help_window

# except:
#  print("error in show_help")

def close_help():
  global help_window
  pass
  try:
    if help_window:
      help_window.close()
      help_window=None
  except:
    print("error in close_help")

if __name__=="__main__":
  import time
#test_call()
  show_help("https://www.mail.ru")
  time.sleep(5)
  close_help()
#test_call()

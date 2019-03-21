import time

def  time_str():
  t = time.localtime()
  time_now = f"{t.tm_hour}:{t.tm_min}"
  return time_now

def list2jsonlist(listt, key):
    for i, item in enumerate(listt):
        listt[i] = {key:item}
    return listt

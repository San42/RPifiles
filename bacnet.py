#!/usr/bin/python3
import BAC0

import time
import sys, os
import bacpypes
sys.path.append('/home/pi/bacpypes')
#sys.path.insert(0, os.path.dirname(bacpypes))
#Disable print

#creating bacnet class to read
class bacnet():
  t1=time.time()
  bac=BAC0.connect()
  t2=time.time()
  def __init__(self,dev_addr,dev_id,point_id):
    self.dev_addr=dev_addr
    self.dev_id=dev_id
    self.point_id=point_id
#read_point()

  def obj_name(self):
    pi=self.point_id
    return pi
#reading a specific point 
  def read_point(self):
    os.system("cd /home/pi/bacpypes ; python3 /home/pi/bacpypes/samples/ReadObjectList.py 100 '10.50.80.3' ")
    in_str=self.dev_addr+' '+self.obj_name()+' '+'presentValue'
    print(in_str)
    curr_val=self.bac.read(in_str)
    print(curr_val)
   # t2=time.time()
    print("Time taken:",self.t2-self.t1)
  def poll_point(self):
    dev=BAC0.device(self.dev_addr,self.dev_id,self.bac)
    #while True :
    dev['Analog Input 4'].poll(delay=1)
    dev.update_history_size(2)
    dev.clear_histories()
    #for i in range(15):
     # time.sleep(1)
    print(dev['Analog Input 4'].history)
    #print('Last Val', dev['Analog Input 4'].lastVal)

b=bacnet('10.50.80.4','150','analogInput 3')
b.poll_point()





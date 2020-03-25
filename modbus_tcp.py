#!/usr/bin/python3
#fix for the imports
import time
import getopt
import datetime
import numpy as np
from pymodbus.client.sync import ModbusTcpClient
from AWSclient import AWSclient
from localdb import localdb
import numpy as np
from pymodbus.constants import Defaults
Defaults.Timeout = 120

#class containing the methods for iterative reading of data and publishing to mqtt
class modbus_tcp():

  aws=AWSclient()
  myAWSIoTMQTTClient=aws.myAWSIoTMQTTClient
  sensor_id=[]
  ip=""
  register=[]
  units=[]
  port=0
  count=1
  ua=1
  type=[]
  cov=[]
  scale=[]
  signed=[]
  conn=aws.conn
  dead =False

  def __init__(self,sensor_id,ip,register,units,port,ua,count,type,cov,scale,signed):
    self.sensor_id=sensor_id
    self.ip=ip
    self.register=register
    self.units=units
    self.port=port
    self.ua=ua
    self.count=count
    self.type=type
    self.cov=cov
    self.scale=scale
    self.signed=signed
    self.publish_to_mqtt()

#Publishing  to mqtt
  def pub(self,timestamp,sensor_id,value,units,type):
    self.aws=AWSclient()
    self.myAWSIoTMQTTClient=self.aws.myAWSIoTMQTTClient
    topic = "NE/RPi"
    msg = '"Time": "{}", "Device":"{}", "Value": "{}","Units":"{}","Type":"{}"'.format(timestamp,sensor_id,value,units,type)
    msg = '{'+msg+'}'
    try:
      self.myAWSIoTMQTTClient.publish(topic, msg, 1)
#      self.myAWSIoTMQTTClient.disconnect()
      print("*****Delivered*****")
    except:
      print('Error at pub')
      pass

  def publish_to_mqtt(self):
    loopCount = 0
    topic = "NE/RPi" #the topic to which mqtt publishes the data
    delay_read=5     #sensor read time delay in seconds
    client = ModbusTcpClient(host=self.ip, port=self.port)
    c=client.connect() #connecting to the modbus device client
    print("***Connection for {} ?:{}***".format(self.ip,c))
    addr=[]
#getting the actual addresses of each register
    for i in range(len(self.register)):
      if int(self.register[i])>=40000:
        t=int(self.register[i])-40001
      elif int(self.register[i])>=30000 and int(self.register[i])<40000:
        t=int(self.register[i])-30001
      else:
        t=int(self.register[i])
      addr.append(t)

#Infinite loop for publishing the data
    try:
       	  while (not self.dead):
                loopCount += 1
                timestamp = datetime.datetime.now()
                mdbs=np.zeros(len(self.register))

#Initializing variables for the values in last read and current read for checking the CoV condition
                if (loopCount==1):
                   last_val=np.zeros(len(self.register))
                new_val=np.zeros(len(self.register))
#publishing  value and details of each register
                for i in range(len(self.register)):
                     if int(self.register[i])>=40000:
                        request = client.read_holding_registers(addr[i],self.count[i], unit=self.ua)
                     else:
                        request = client.read_input_registers(addr[i],self.count[i], unit=self.ua)
                     try:
                       print(request.registers[0])
                       mdbs[i]=request.registers[0]*self.scale[i]
                       if self.signed[i]!=1:
                         if mdbs[i]>32767:
                            mdbs[i]=mdbs[i]-65535
                     except:
                       print('Error 5')
                       pass
                     print(' Loop# {:d}'.format(loopCount))
                     print(' Time: {} \nDevice: {} \n'.format(timestamp,self.sensor_id))
                     print(' Value :{}\n'.format(mdbs[i]))
#                     print("tcp Number of threads:",threading.active_count()) 
#Storing the current and the last value for CoV conditions
                     if loopCount==1:
                       last_val[i]=mdbs[i]
                       new_val[i]=mdbs[i]
                     else:
                       new_val[i]=mdbs[i]
#print('last: {}, current:{}'.format(last_val[i],new_val[i]))
#Publishing the data if Change of Value condition is satisfied
                     try:
                       if (abs(float(new_val[i])-float(last_val[i]))>self.cov[i]):
                         print("Value greater than CoV")
                         self.pub(timestamp,self.sensor_id[i],mdbs[i],self.units[i],self.type[i])
                     except ZeroDivisionError:
                       print(float('inf'))
#Publishing values after every 5 iteration i.e 5*5=25 sec
                     if(loopCount%12==0):
#Writing in the local database
                        if localdb.conn=='1':
                           try:
                            self.pub(timestamp,self.sensor_id[i],mdbs[i],self.units[i],self.type[i]) #publishing the data to aws mqtt
                            localdb().write_to_localdb(timestamp,self.sensor_id[i],mdbs[i],self.units[i],self.type[i],'1','1')
                            localdb().publish_to_mqtt()
                            print('tcp localdb written')
                           except KeyboardInterrupt:
                            print("Error 2")
                            pass
                        else:
                            localdb().write_to_localdb(timestamp,self.sensor_id[i],mdbs[i],self.units[i],self.type[i],'0','0') #writing to the local postgres database when offline
                            print("tcp OFFLINE $$$$$$$")
                last_val=new_val
                client.close()
                time.sleep(delay_read)
    except KeyboardInterrupt:
      	  pass
    print('Exiting the loop')
    self.myAWSIoTMQTTClient.disconnect()
    print('Disconnected from AWS')
#modbus_tcp([101,102,103],"10.20.0.188",[30001,30002,30003],["C","C","F"],502,1,1,["Temp","Temp","Temp"],[.1,.1,.1],[1,1,1],[1,1,1])

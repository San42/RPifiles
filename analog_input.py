#!/usr/bin/python3
#fix for the imports
import time
import getopt
import datetime
from  AWSclient import AWSclient
from picubes import picubes
from localdb import localdb
import threading
picubes = picubes()

#class containing the methods for iterative reading of data and publishing to mqtt
class analog_input():
#Defining the parameters for the class instance
  sensor_id=0 # sensor id number
  u=0 #Unit of the data
  module=0 # picube module number
  inputn=0 #picubes input slot number UI
  type="" # picubes input type(resistance, voltage... etc)
  cov=0  # change of  value fraction/percentage
#creating instances of the AWS IoT client 
  aws=AWSclient()
  myAWSIoTMQTTClient=aws.myAWSIoTMQTTClient
  dead=False

  def __init__(self,sensor_id,u,module,inputn,type,cov):
      self.sensor_id=sensor_id
      self.u=u
      self.module=module
      self.inputn=inputn
      self.type=type
      self.cov=cov
      self.publish_to_mqtt()

# Function to publish the data to a mqtt topic
  def pub(self,timestamp,sensor_id,s,units,type):
      topic = "NE/RPi"
      msg = '"Time": "{}", "Device":"{}", "Value": "{}","Units":"{}","Type":"{}"'.format(timestamp,sensor_id,s,units,type)
      msg = '{'+msg+'}'
#Publishing the data in a JSON format to mqtt
      self.myAWSIoTMQTTClient.publish(topic, msg, 1)
 #     print("published")

#Function to read the sensor data according to the arguments and then call the pub() function for publishing to mqtt
  def publish_to_mqtt(self):
     loopCount = 0
#the publishing time delay in seconds
     delay_read = 5
#     curr_online=1

#Infinite loop for publishing the data
     try:
          while(not self.dead):
                  loopCount += 1
                  if loopCount==1:
                     last_val=[] 
                  new_val=[]

#checking the type of the data to be obtained from the sensors using the  picubes module 
                  for j in range(len(self.sensor_id)):
                    if self.type[j]==0:
                       tp="Resistance"
                       t=picubes.readUI(self.module[j],self.inputn[j],self.type[j])
                    elif self.type[j]==1:
                       tp="Digital"
                       t=picubes.readUI(self.module[j],self.inputn[j],self.type[j])
                    elif self.type[j]==2:
                       tp="Voltage/Current in %"
                       t=picubes.readUI(self.module[j],self.inputn[j],self.type[j])
                    elif self.type[j]==3:
                       tp="Temperature"
                       t = picubes.readUI(self.module[j],self.inputn[j],self.type[j])*.01
                    elif self.type[j]==4:
                       tp="Pulse"
                       t = picubes.readUI(self.module[j],self.inputn[j],self.type[j])
                    timestamp = datetime.datetime.now()
                    print('Sensor id: {},  Loop : {}'.format(self.sensor_id[j],loopCount))
                    print(' Time: {} \n'.format(timestamp))
                    print('{} : {}\n'.format(tp,t))
                    print("ai Number of threads:",threading.active_count()) 
#Storing the current and the last value for CoV conditions
                    if loopCount==1:
                      last_val.append(t)
                      new_val.append(t)
                    else:
                      new_val.append(t)
                      #print('last: "{}", current:"{}"'.format(last_val,new_val))
#Publishing the data if Change of Value condition is satisfied
#                      if (abs(float(new_val[j])-float(last_val[j]))/(float(last_val[j]))>cov[j]):
#                         print("Value greater than CoV")
#                         pub(timestamp,sensor_id[j],t,u[j],tp)
#Publishing values after every 5 iteration i.e 5*5=25 sec
                    if(loopCount%20==0):
                       if localdb().conn=='1':
                         try:
                            self.pub(timestamp,self.sensor_id[j],t,self.u[j],tp)
                            localdb().write_to_localdb(timestamp,self.sensor_id[j],t,self.u[j],tp,'1','1')
                         except:
                            pass
                       else:
                         localdb().write_to_localdb(timestamp,self.sensor_id[j],t,self.u[j],tp,'0','0')
                         print('%%%%%%%%%OFFLINE localdb ai%%%%%%%%%%%%%')

                  last_val=new_val
                  print('Sleeping...')
#Reading values from sensor every delay_read(=5) sec
                  time.sleep(delay_read)
     except KeyboardInterrupt:
          pass
     print('Exiting the loop')
     self.myAWSIoTMQTTClient.disconnect()
     print('Disconnected from AWS')
#anlg=analog_input([150601],["C"],[2],[4],[3],[.05])



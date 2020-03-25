#!/usr/bin/python3
#Code to call each of the three coonectors(rtu,tcp and ai) in multiple threads after reading the JSON file
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import json
from collections import OrderedDict
import threading, time
#inserting directory for other python scripts
sys.path.append('/home/pi/AWS')
from modbus_rtu import modbus_rtu
from modbus_tcp import modbus_tcp
from analog_input import analog_input
from multiprocessing import Process
from pymodbus.client.sync import ModbusTcpClient
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import logging

#the main connector class
class rtu():
  thread1=[]
#Function to pass the arguments to the rtu connector
  def registers_rtu(self,serial_no,baud_rate,par,byte_size,stop_bits,dev_no,dev_id,mdbus ):
#getting the number of registers
        l=[]
        for m1 in mdbus:
           i=0
           for m2 in m1:
             i=i+1
             
           l.append(i)
#initializing the 2-D arrays to store the details of each register on different columns . Rows----> devices(boilers) , columns----> register values
        snsr_id=(np.zeros((len(mdbus),max(l)))).astype(str)
        rgstr=(np.zeros((len(mdbus),max(l)))).astype(str)
        units=(np.zeros((len(mdbus),max(l)))).astype(str)
        name=(np.zeros((len(mdbus),max(l)))).astype(str)
        type=(np.zeros((len(mdbus),max(l)))).astype(str)
        count=(np.zeros((len(mdbus),max(l)))).astype(str)
        cov=(np.zeros((len(mdbus),max(l)))).astype(str)
        scale=(np.zeros((len(mdbus),max(l)))).astype(str)
        signed=(np.zeros((len(mdbus),max(l)))).astype(str)
        i=0
        for m1 in mdbus:
           j=0
           for m2 in m1:
             rgstr[i,j]=m2
             name[i,j]=m1[m2]["name"]
             type[i,j]=m1[m2]["type"]
             units[i,j]=m1[m2]["units"]
             count[i,j]=m1[m2]["count"]
             cov[i,j]=m1[m2]["CoV"]
             snsr_id[i,j]=m1[m2]["sensor_id"]
             scale[i,j]=m1[m2]["scale"]
             signed[i,j]=m1[m2]["signed"]
             j=j+1
           i=i+1
        time.sleep(0.2)
#        print("****In register_rtu******")
        modbus_rtu(serial_no,snsr_id,stop_bits,byte_size,par,baud_rate,rgstr,count,dev_no,cov,units,type,scale,signed,name)

  def run(self):
     with open('/home/pi/python3_venv/AWS/config.txt') as specs:
      data=json.load(specs,object_pairs_hook=OrderedDict) #storing the contents of JSON config file keeping the order intact
#      print("^^^^^^^^^^^^^^^^change^^^^^^^^^^^^^",data["Specs"]["analog_input"]["Boiler2"]["sensors"]["sensor1"]["sensor_id"])
      specs=data["Specs"]
#Looping through the JSON config file contents
      for con in specs:
#Checking for all the devices under modbus RTU and storing the details in different arrays
        if con=="modbus_rtu":
          ports=[]
          serial_no=[]
          parity=[]
          data_bits=[]
          stop_bits=[]
          baud_rate=[]
          j=0
          for  p in data["Specs"]["modbus_rtu"]:
            ports.append(p)
#Iterating through each port and storing the details
          for p in ports :
            dev=[]
            serial_no.append(data["Specs"]["modbus_rtu"][p]["serial_no"])
            baud_rate.append(data["Specs"]["modbus_rtu"][p]["baud_rate"])
            parity.append(data["Specs"]["modbus_rtu"][p]["parity"])
            data_bits.append(data["Specs"]["modbus_rtu"][p]["data_bits"])
            stop_bits.append(data["Specs"]["modbus_rtu"][p]["stop_bits"])
            for d in data["Specs"]["modbus_rtu"][p]["Devices"]:
              dev.append(d)
            dev_no=[]
            dev_id=[]
            json_rgstr=[]
            boilers_rtu=[]
#Iterating through all the devices in each port
            for d in dev:
               dev_no.append(data["Specs"]["modbus_rtu"][p]["Devices"][d]["device_no"])
               dev_id.append(data["Specs"]["modbus_rtu"][p]["Devices"][d]["device_id"])
               boilers_rtu.append(d)
               json_rgstr.append(data["Specs"]["modbus_rtu"][p]["Devices"][d]["registers"])
               self.thread1.append(threading.Thread(target=self.registers_rtu,args=(serial_no[j],baud_rate[j],parity[j],data_bits[j],stop_bits[j],dev_no,dev_id,json_rgstr)))
#Creating threads for each port
            j=j+1
class tcp():

#  logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-9s) %(message)s',)
  thread2=[]
#Function to pass the arguments to the tcp connector
  def registers_tcp(self,mdbus,ip1,p,ua):
#        logging.debug('Starting')
        snsr_id=[]
        rgstr=[]
        units=[]
        name=[]
        type=[]
        count=[]
        cov=[]
        measure=[]
        scale=[]
        signed=[]
#Looping through the registers  and storing the values in different arrays
        for r in mdbus:
           rgstr.append(r)
           name.append(mdbus[r]["name"])
           type.append(mdbus[r]["type"])
           units.append(mdbus[r]["units"])
           count.append(mdbus[r]["count"])
           cov.append(mdbus[r]["CoV"])
           snsr_id.append(mdbus[r]["sensor_id"])
           measure.append(mdbus[r]["Measure"])
           scale.append(mdbus[r]["scale"])
           signed.append(mdbus[r]["signed"])
        time.sleep(.2)
#Calling the modbus_tcp connector script with the necessary arguments
        modbus_tcp(snsr_id,ip1,rgstr,units,p,ua,count,measure,cov,scale,signed)
  def run(self):
     with open('/home/pi/python3_venv/AWS/config.txt') as specs:
      data=json.load(specs,object_pairs_hook=OrderedDict) #storing the contents of JSON config file keeping the order intact
#      print("^^^^^^^^^^^^^^^^change^^^^^^^^^^^^^",data["Specs"]["analog_input"]["Boiler2"]["sensors"]["sensor1"]["sensor_id"])
      specs=data["Specs"]
#Looping through the JSON config file contents
      for con in specs:
#Opening the JSON config file containing the device and sensor details
#Checking for all the devices under modbus tcp and storing the details in different arrays
        if con=="modbus_tcp":
          boilers_tcp=[]
          ip=[]
          port=[]
          dev_id=[]
          u=[]
          json_rgstr=[]
          for b in data["Specs"]["modbus_tcp"]:
            ip.append(data["Specs"]["modbus_tcp"][b]["ip_address"])
            port.append(data["Specs"]["modbus_tcp"][b]["port"])
            dev_id.append(data["Specs"]["modbus_tcp"][b]["device_id"])
            u.append(data["Specs"]["modbus_tcp"][b]["unit_address"])
            boilers_tcp.append(b)
#storing the details of each register for all the devices/boilers under tcp in an array
          for i in range(len(boilers_tcp)):
            json_rgstr.append(data["Specs"]["modbus_tcp"][boilers_tcp[i]]["registers"])
         
#array to create multiple threads for each device/ boiler data under tcp(number of threads = number of boilers)
          for i in range(len(json_rgstr)):
               self.thread2.append(threading.Thread(target=self.registers_tcp,args=(json_rgstr[i],ip[i],port[i],u[i])))

class ai():

  thread3=[]
#Function to pass the arguments to the analog input connector
  def sensors_ai(self,snsrs,dev_id):
        snsr_id=[]
        units=[]
        name=[]
        module=[]
        input_no=[]
        type=[]
        cov=[]
        for d in snsrs:
           snsr_id.append(snsrs[d]["sensor_id"])
           units.append(snsrs[d]["units"])
           name.append(snsrs[d]["name"])
           module.append(snsrs[d]["module"])
           input_no.append(snsrs[d]["input_no"])
           cov.append(snsrs[d]["CoV"])
           type.append(snsrs[d]["type"])
        time.sleep(.2)
#Calling the analog_input connector script with the necessary arguments
        analog_input(snsr_id,units,module,input_no,type,cov)
  def run(self):
#storing the details of each device/boiler under analog input in an array and passing them to the "sensors_ai" function
     with open('/home/pi/python3_venv/AWS/config.txt') as specs:
      data=json.load(specs,object_pairs_hook=OrderedDict) #storing the contents of JSON config file keeping the order intact
#      print("^^^^^^^^^^^^^^^^change^^^^^^^^^^^^^",data["Specs"]["analog_input"]["Boiler2"]["sensors"]["sensor1"]["sensor_id"])
      specs=data["Specs"]
#Looping through the JSON config file contents
      for con in specs:
#Opening the JSON config file containing the device and sensor details

        if con=="analog_input":
          boilers_ai=[]
          dev_id=[]
          for b in data["Specs"]["analog_input"]:
            boilers_ai.append(b)
            dev_id.append(data["Specs"]["analog_input"][b]["device_id"])
          json_sensors=[]
#storing the sensor details in JSON format in the variable "json_sensors"
          for i in range(len(boilers_ai)):
            json_sensors.append(data["Specs"]["analog_input"][boilers_ai[i]]["sensors"])
#array to create multiple threads for each device/ boiler data under analog input(number of threads = number of boilers)
          for i in range(len(json_sensors)):
               self.thread3.append(threading.Thread(target=self.sensors_ai,args=(json_sensors[i],dev_id[i])))
rtu().run()
print(len(rtu().thread1))
for thread1 in rtu().thread1:
  thread1.start()
tcp().run()
for thread2 in tcp().thread2:
  thread2.start()
ai().run()
for thread3 in ai().thread3:
  thread3.start()
#while True:
#    print("Number of threads:",threading.active_count())
time.sleep(1)

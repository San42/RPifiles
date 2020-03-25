#!/usr/bin/python3
#Script to write write data in a local influx db and publish the unpublished data when internet connection is restored
import time
import socket
import psycopg2
from AWSclient import AWSclient

class localdb:
  aws=AWSclient()
  myAWSIoTMQTTClient=aws.myAWSIoTMQTTClient
  conn=aws.conn #variable for getting the connection status to AWS server
  if conn==True:
    conn='1'
  else:
    conn='0'

#Function to write the data into a local influx db
  def write_to_localdb(self,timestamp,sensor_id,s,units,type,online,published):
     conn = psycopg2.connect("dbname=sensor_data user=postgres password=15cs420 host=localhost")
     cur=conn.cursor()
     cur.execute("insert into ne_boiler_test values (%s,%s,%s,%s,%s,%s,%s)",(sensor_id,s,timestamp,type,units,online,published))
     conn.commit()
#Function to publish  to AWS mqtt
  def pub(self,timestamp,sensor_id,value,units,type):
     topic = "NE/RPi"
     msg = '"Time": "{}", "Device":"{}", "Value": "{}","Units":"{}","Type":"{}"'.format(timestamp,sensor_id,value,units,type)
     msg = '{'+msg+'}'
     self.myAWSIoTMQTTClient.publish(topic, msg, 1)

#publishing the data to AWS mqtt which  weren't published
  def publish_to_mqtt(self):
     conn = psycopg2.connect("dbname=sensor_data user=postgres password=15cs420 host=localhost")
     cur=conn.cursor()
     cur.execute("select * from ne_boiler_test where online='0' and published='0'")
     data=cur.fetchall()
     print("%%%%%%%%%%%%%%length of data",len(data))
     for i in range(len(data)):
         sensor_id=data[i][0]
         value=data[i][1]
         timestamp=data[i][2]
         type=data[i][3]
         units=data[i][4]
         try:
           print("#######unpublished**********", timestamp,sensor_id,value,units,type)
           self.pub(timestamp,sensor_id,value,units,type)
           cur.execute("update ne_boiler_test set published='1' where timestamp=%s and sensor_id=%s",(timestamp,sensor_id))
           conn.commit()
         except:
           pass


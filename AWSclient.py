#!/usr/bin/python3
#fix for the imports
import os
import sys
import ssl
import AWSIoTPythonSDK
#including paths of directories containing AWS client files
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
sys.path.append('/home/pi/aws-iot-device-sdk-python/samples/basicPubSub')
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import getopt
import datetime

class AWSclient():
# Custom MQTT message callback
  def customCallback(self,client, userdata, message):
     print("Received a new message: ")
     print(message.payload)
     print("from topic: ")
     print(message.topic)
     print("--------------\n\n")
  useWebsocket = False
  logger = None
  myAWSIoTMQTTClient = None
  conn=None
#storing the paths to the hosts and the certificates(downloaded from AWS) 
  host ="a3n4bo1x3cchnu-ats.iot.us-east-1.amazonaws.com" 
  rootCAPath = "/home/pi/certs1/Amazon_Root_CA_1.pem"
  certificatePath = "/home/pi/certs1/c663b9569c-certificate.pem.crt"
  privateKeyPath = "/home/pi/certs1/c663b9569c-private.pem.key"
# Init AWSIoTMQTTClient
  def __init__(self):
     self.configure_logging()
     if self.useWebsocket:
        self.myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
        self.myAWSIoTMQTTClient.configureEndpoint(self.host, 443)
        self.myAWSIoTMQTTClient.configureCredentials(self.rootCAPath)
     else:
        self.myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
        self.myAWSIoTMQTTClient.configureEndpoint(self.host, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)
# AWSIoTMQTTClient connection configuration
     self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
     self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
     self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
     self.time_out= self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(180)  # 10 sec
     self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(180)  # 5 sec
# Connect and subscribe to AWS IoT
     try:
       self.conn=self.myAWSIoTMQTTClient.connect()
     except:
       pass

  def  configure_logging(self):
# Configure logging
     if sys.version_info[0] == 3:
        self.logger = logging.getLogger("core")  # Python 3
     else:
        self.logger = logging.getLogger("AWSIoTPythonSDK.core")  # Python 2
     self.logger.setLevel(logging.DEBUG)
     streamHandler = logging.StreamHandler()
     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     streamHandler.setFormatter(formatter)
     self.logger.addHandler(streamHandler)

  def AWSIoTClient(self):
     return self.myAWSIoTMQTTClient

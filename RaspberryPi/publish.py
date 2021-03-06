import smbus
import json
import time
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


################AWS MQTT SET-UP#############################
##The following code is adapted from the documentation for##
##the AWS-IoT SDK found under https://github.com/aws/aws/ ##
##iot-device-sdk-python/blob/master/README.rst            ##
############################################################
host = "apofivg2u2bsg-ats.iot.eu-west-2.amazonaws.com"
topic = "IC.embedded/fabric/data"

myMQTTClient = AWSIoTMQTTClient("MyClientId") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint(host, 8883)
certPath = '/home/pi/AWS/'
myMQTTClient.configureCredentials("{}root-ca.pem".format(certPath), "{}cloud.pem.key".format(certPath), "{}cloud.pem.crt".format(certPath)) 

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec

myMQTTClient.connect()


##################Sensor Set-Up####################
bus = smbus.SMBus(1)                #bus for air quality sensor
bus2 = smbus.SMBus(1)		    #bus2 for temp and humid sensor
#printing initial status
print("Initial Status: ", bus.read_i2c_block_data(0x5b,0x00,1))
emptylist = []
bus.write_i2c_block_data(0x5b, 0xf4,emptylist)
print("Written the empty list to 0xf4")
print("Status is now: ", bus.read_i2c_block_data(0x5b,0x00,1))
print("ErrorID is: ", bus.read_i2c_block_data(0x5b, 0xe0,1))
#setting mode to be 100
mode = [0b100]
mode[0]=mode[0]<<4
bus.write_i2c_block_data(0x5b,0x01,mode)


while True:
	bus2.write_byte(0x40,0xF5)        #0xF5 is the command for taking measurements for humidity
	time.sleep(0.25)
	data0 = bus2.read_byte(0x40)       #reading MS-Byte of data
	data1 = bus2.read_byte(0x40)       #reading LS-Byte of data
	humidity = ((data0*256+data1)*125/65536.0)      #conversion of data into meaningful values(calculation given by datasheet)

	bus2.write_byte(0x40,0xF3)         #0xF3 is the command for taking measurements for temperature
	time.sleep(0.65)
	data0 = bus2.read_byte(0x40)        #reading MS-Byte of data
	data1 = bus2.read_byte(0x40)        #reading LS-Byte of data
	temperature = ((data0*256+data1)*175.72/65536.0)-46.85        #conversion of data into meaningful values(calculation given by datasheet)	
	
	#data01 and data23 are humidity and temperature values used for compensating the air quality sensor
	data01 = round(humidity/512)

	tdata=temperature
	if temperature>75:
		tdata=75
	if temperature<-25:
		tdata=-25
	data23 = round((tdata+25)*2.55)
	
	#writing humidity and temperature values onto ENV_DATA address
	bus.write_i2c_block_data(0x5b,0x05,[data01,0x00,data23,0x00])
	
        #reading 4 bytes of data
	data = bus.read_i2c_block_data(0x5b,0x02,4)
	co2data = (data[0]<<8)+data[1]         #MS two bytes are co2 data
	TVOCdata = (data[2]<<8)+data[3]        #LS two bytes are tvoc data
	
	humid = float("%.1f" % humidity)
	temp = float("%.1f" % temperature)
	current_time = time.time()
	
	#publishing json data onto topic
	jsonData =json.dumps({"time":current_time,"co2":co2data,"TVOC":TVOCdata, "humidity":humid, "temperature":temp})
	
	myMQTTClient.publish(topic,jsonData,1)

	print("Published: %s\n" %(jsonData))
	time.sleep(0.1)
myMQTTClient.disconnect()

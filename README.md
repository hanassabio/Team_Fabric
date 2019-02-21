# WorkAir by Team Fabric

This repository contains the code for our IoT sensor based on the RaspberryPi as well as the WebApp created to display live and historical data. 

### Raspberry-Pi Code
The raspberry pi file **publish.py** sets up the connection to the AWS IoT broker, sets up the sensors, and then publishes sensor readings once per second. The file is run on boot.

### Web-App Code
The code for the web-app is divided into 3 sections which correspond to the different sections of the web-app. 
1) **main.html** is the main page of web application and contains iframes of the other two sections.
2) **live.html** is the "Live" page of the of the web application which sets up the connection to the AWS MQTT broker and displays live sensor readings as well as live graphs of the most recent readings. 
3) **history.html** is the "History" page of the web application and contains iframes of graphs of historical data stored in the AWS database, visualized using Splunk. 


### Marketing Website
The marketing website is accessible at this adress : https://givearn.wixsite.com/workair

import paho.mqtt.publish as publish
import dht11
import time
import RPi.GPIO as GPIO

soilSensorPin = 21
dht11Pin = dht11.DHT11(pin=17)
GPIO.setmode(GPIO.BCM)
GPIO.setup(soilSensorPin, GPIO.IN)
dhtresult = dht11Pin.read()

#publishes temp, humidity, and soilstatus every 5 secs
while True:

    #Displays temp and humidity if the input is valid
    if dhtresult.is_valid():
        temperature = str(dhtresult.temperature)[:5] 
        farenheit = str((dhtresult.temperature* 9/5) + 32)[:5] 
        humidity = str(dhtresult.humidity) + "%"

    #Displays error message when the input is invalid
    else:
        temperature = "Sensor error, please refresh page"
        farenheit = " "
        humidity = "Sensor error, please refresh page"

    #Detects soil moisture
    if GPIO.input(soilSensorPin):
        soilStatus = "No water detected"
    else:
        soilStatus = "Water detected"

    sendString = str(temperature + "," + farenheit + "," + humidity + "," + soilStatus)

    publish.single("IOTWateringLab/telemetry", payload=sendString, hostname="test.mosquitto.org")
    print("Sent message: " + sendString)


    #wait 5 seconds before sending another message

    time.sleep(5)
    
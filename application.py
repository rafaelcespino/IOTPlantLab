from flask import Flask, session, render_template, request, redirect, url_for
import RPi.GPIO as GPIO
import time
import sys
import dht11

app=Flask(__name__)
GPIO.setwarnings(False)
GPIO.cleanup()


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        
        soilSensorPin = 21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(soilSensorPin, GPIO.IN)

        #Detects soil moisture
        if GPIO.input(soilSensorPin):
            soilStatus = "No water detected"
        else:
            soilStatus = "Water detected"

        #activates pump on button press
        pumpTime = int(request.form.get("pumpTime"))
        pump_pin = 23
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(pump_pin, GPIO.LOW)
        time.sleep(pumpTime)
        GPIO.output(pump_pin, GPIO.HIGH)


        return render_template("index.html", soilStatus=soilStatus)

    elif request.method == "GET":
        #GPIO Setup
        soilSensorPin = 21
        dht11Pin = dht11.DHT11(pin=17)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(soilSensorPin, GPIO.IN)
        dhtresult = dht11Pin.read()


        temperature = dhtresult.temperature
        farenheit = (dhtresult.temperature* 9/5) + 32
        humidity = dhtresult.humidity

        #Detects soil moisture
        if GPIO.input(soilSensorPin):
            soilStatus = "No water detected"
        else:
            soilStatus = "Water detected"

    

    return render_template("index.html", soilStatus=soilStatus, temperature=temperature, humidity=humidity, farenheit=farenheit)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
from flask import Flask, session, render_template, request, redirect, url_for
import RPi.GPIO as GPIO
import time
import sys
import dht11
import threading


GPIO.setwarnings(False)
GPIO.cleanup()

def waterLoop(delay):
    #while(True):
        #pumpTime = 5
        #pump_pin = 23
        #GPIO.setup(23, GPIO.OUT)
        #GPIO.output(pump_pin, GPIO.LOW)
        #time.sleep(pumpTime)
        #GPIO.output(pump_pin, GPIO.HIGH)
        #secondsDelay = delay * 3600
    while(True):
        print("Delay finished")
        time.sleep(delay)

app=Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        GPIO.setmode(GPIO.BCM)
        #activates pump if user decided to activate pump once
        if request.form["option"] == "pump":
            pumpTime = int(request.form.get("pumpTime"))
            pump_pin = 23
            GPIO.setup(23, GPIO.OUT)
            GPIO.output(pump_pin, GPIO.LOW)
            time.sleep(pumpTime)
            GPIO.output(pump_pin, GPIO.HIGH)

        #creates a thread to run watering schedule if the user decided to start a schedule
        elif request.form["option"] == "schedule":
            print("starting thread")
            delay = request.form.get("scheduleDelay")
            t = threading.Thread(target=waterLoop, name="running schedule", args=(delay))
            t.daemon = True #thread will be closed when the server closes as well 
            t.start()


        #Redirects to index using GET request after activating pump or starting schedule
        return redirect(url_for("index"))

    elif request.method == "GET":
        #GPIO Setup
        soilSensorPin = 21
        dht11Pin = dht11.DHT11(pin=17)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(soilSensorPin, GPIO.IN)
        dhtresult = dht11Pin.read()

        #Displays temp and humidity if the input is valid
        if dhtresult.is_valid():
            temperature = str(dhtresult.temperature)[:5] + "°C /"
            farenheit = str((dhtresult.temperature* 9/5) + 32)[:5] + "°F"
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

    
    #renders HTML template on GET request with the calculated values 
    return render_template("index.html", soilStatus=soilStatus, temperature=temperature, humidity=humidity, farenheit=farenheit)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)

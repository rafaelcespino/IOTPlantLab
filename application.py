from flask import Flask, session, render_template, request, redirect, url_for
import RPi.GPIO as GPIO
import time
import sys
import dht11
import threading
import requests


GPIO.setwarnings(False)
GPIO.cleanup()

def waterLoop(delay, timeType, pumpTime, iterations):
    #while(True):
        #pumpTime = 5
        #pump_pin = 23
        #GPIO.setup(23, GPIO.OUT)
        #GPIO.output(pump_pin, GPIO.LOW)
        #time.sleep(pumpTime)
        #GPIO.output(pump_pin, GPIO.HIGH)
        #secondsDelay = delay * 3600
    for i in range(int(iterations)):
        print("Delay finished")
        GPIO.setmode(GPIO.BCM)
        #activates pump if user decided to activate pump once
        pump_pin = 23
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(pump_pin, GPIO.LOW)
        time.sleep(int(pumpTime))
        GPIO.output(pump_pin, GPIO.HIGH)
        if timeType=="minutes":
            delay*=60
        elif timeType == "hours":
            delay*3600
        time.sleep(int(delay))

app=Flask(__name__)

@app.route("/", methods=["GET"])
def index():

    zipCode = 75035
    API = "908b6bab23b7dc66f92948681f48692f"
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?zip={zipCode},us&units=imperial&appid={API}")
    data = response.json()
    cityName = data.get('name')
    weatherConditionId = ((data["weather"])[0])["id"]

    switcher = {
            200: f"There is currently a thunderstorm with light rain happening in {cityName}.",
            201: f"There is currently a thunderstorm with moderate rain happening in {cityName}.",
            202: f"There is currently a thunderstorm with heavy rain happening in {cityName}.",
            210: f"There is currently a light thunderstorm happening in {cityName}.",
            211: f"There is currently a thunderstorm happening in {cityName}.",
            212: f"There is currently a heavy thunderstorm happening in {cityName}.",
            221: f"There is currently a ragged thunderstorm happening in {cityName}.",
            230: f"There is currently a thunderstorm with light drizzle happening in {cityName}.",
            231: f"There is currently a thunderstorm with moderate drizzle happening in {cityName}.",
            232: f"There is currently a thunderstorm with heavy drizzle happening in {cityName}.",

            300: f"There is currently a light drizzle in {cityName}.",
            301: f"There is currently a moderate drizzle in {cityName}.",
            302: f"There is currently a heavy drizzle in {cityName}.",
            310: f"There is currently a light drizzle in {cityName}.",
            311: f"There is currently a moderate drizzle in {cityName}.",
            312: f"There is currently a heavy drizzle in {cityName}.",
            313: f"There is currently a light drizzle in {cityName}.",
            314: f"There is currently a moderate drizzle in {cityName}.",
            321: f"There is currently a heavy drizzle in {cityName}.",

            500: f"It's currently raining lightly in {cityName}.",
            501: f"It's currently raining in {cityName}.",
            502: f"It's currently raining heavily in {cityName}.",
            503: f"It's currently raining very heavily in {cityName}.",
            504: f"It's currently raining extremely heavily in {cityName}.",
            511: f"There is currently freezing rain in {cityName}.",
            520: f"There are currently light showers in {cityName}.",
            521: f"There are currently showers in {cityName}.",
            522: f"There are currently heavy showers in {cityName}.",
            531: f"There are currently ragged showers in {cityName}.",

            600: f"It's currently snowing lightly in {cityName}.",
            601: f"It's currently snowing in {cityName}.",
            602: f"It's currently snowing heavily in {cityName}.",
            611: f"It's currently sleeting in {cityName}.",
            612: f"There is currently a light shower sleet in {cityName}.",
            613: f"There is currently a shower sleet in {cityName}.",
            615: f"There is currently light rain and snow in {cityName}.",
            616: f"There is currently rain and snow in {cityName}.",
            620: f"There is currently a light shower of snow in {cityName}.",
            621: f"There is currently a shower of snow in {cityName}.",
            622: f"There is currently a heavy shower of snow in {cityName}.",

            701: f"It's currently misting in {cityName}.",
            711: f"There is currently smoke in {cityName}.",
            721: f"There is currently haze in {cityName}.",
            731: f"There is currently dust in {cityName}.",
            741: f"It's currently foggy in {cityName}.",
            751: f"It's currently sandy in {cityName}.",
            761: f"It's currently dusty in {cityName}.",
            762: f"There is currently ash in {cityName}.",
            771: f"There is currently a squall in {cityName}.",
            781: f"A tornado has been reported in {cityName}. Seek shelter immediately.",

            800: f"It's currently clear in {cityName}.",

            801: f"It's currently cloudy in {cityName}.",
            802: f"It's currently cloudy in {cityName}.",
            803: f"It's currently cloudy in {cityName}.",
            804: f"There is currently an overcast in {cityName}.",
        }
    condition = switcher.get(weatherConditionId, "Invalid data.")
    

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
    return render_template("index.html", soilStatus=soilStatus, temperature=temperature, humidity=humidity, farenheit=farenheit, condition=condition)

@app.route("/water", methods=["POST"])
def water():
    GPIO.setmode(GPIO.BCM)
    #activates pump if user decided to activate pump once
    
    pumpTime = int(request.form.get("pumpTime"))
    pump_pin = 23
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(pump_pin, GPIO.LOW)
    time.sleep(pumpTime)
    GPIO.output(pump_pin, GPIO.HIGH)

    return redirect(url_for("index"))

@app.route("/schedule", methods=["POST"])
def schedule():
    #creates a thread to run watering schedule if the user decided to start a schedule
    print("starting thread")
    delay = request.form.get("scheduleDelay")
    timeType = request.form.get("timeType")
    pumpTime = request.form.get("pumpTime")
    iterations = request.form.get("iterations")
    scheduleThread = threading.Thread(target=waterLoop, name="running schedule", args=[int(delay), timeType, int(pumpTime), int(iterations)])
    scheduleThread.setDaemon(True) #thread will be closed when the server closes as well 
    scheduleThread.start()

    return redirect(url_for("index"))


    
    
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)

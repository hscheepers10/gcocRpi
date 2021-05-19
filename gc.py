from board import *
from datetime import datetime
import RPi.GPIO as GPIO
import adafruit_dht
import sys
import mariadb
import time
import os

startTime = time.time()
now = datetime.now()

#DHT sensor pins.  
SENSOR_PIN_1 = D4   #GPIO4  sensor 1.  
SENSOR_PIN_2 = D18  #GPIO18 sensor 2.  

#////////////////////////FAN METHODS////////////////////////.  
#fan On1
def fanOn1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.LOW)
    print("|  Fan 1 On")
    
#fan Off1
def fanOff1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.HIGH)
    print("|  Fan 1 Off")

#fan On2
def fanOn2():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.output(20, GPIO.LOW)
    print("|  Fan 2 On")
    
#fan Off2
def fanOff2():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.output(20, GPIO.HIGH)
    print("|  Fan 2 Off")

# #fan On3
# def fanOn3():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(17, GPIO.OUT)
#     GPIO.output(17, GPIO.LOW)
#     print("|  Fan 3 On")
#     
# #fan Off3
# def fanOff3():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(17, GPIO.OUT)
#     GPIO.output(17, GPIO.HIGH)
#     print("|  Fan 3 Off")
    
#Converting seconds passed to hours/min/sec.  
def timeConvert(sec):
    min = sec // 60
    sec = sec % 60
    hours = min // 60
    min = min % 60
    timeString = "{0}:{1}:{2}".format(int(hours),int(min),int(sec))
    print("|  Oven 1 has been running for "+timeString+" hours")
    
def timeDBConvert(sec):
    min = sec // 60
    sec = sec % 60
    hours = min // 60
    min = min % 60
    timeDBConvert = "{0}:{1}:{2}".format(int(hours),int(min),int(sec))
    return timeDBConvert

def getStat(t):
    if(t >= 30):
        string = "Fans are On"
    if(t < 30):
        string = "Fans are Off"
    return string

#////////////////////////LOOP.////////////////////////  
while True:
    endTime = time.time()
    #Initialising sensor state.  
    dht22_1 = adafruit_dht.DHT22(SENSOR_PIN_1, use_pulseio=False)
    dht22_2 = adafruit_dht.DHT22(SENSOR_PIN_2, use_pulseio=False)

    #--------------------------Try Catch for sensor 1----------------------------
    
    print("----------------------------------------------------------------------------")
    try:
        temperature1 = dht22_1.temperature
        humidity1 = dht22_1.humidity
        print("|  Temp1: {:.1f}C*    Humid1: {}%".format(temperature1,humidity1))
        temp1 = int(temperature1)
        hum1 = int(humidity1)
        
        if(temp1 is None):
            continue
            print("|  No reading receivied, fans will remain as is.  ")
        
        if(temp1 >= 50):
            fanOn1()
            
        if(temp1 < 50):
            fanOff1()

    except RuntimeError as error:
        temp1 = 0
        hum1 = 0
        print("|  Sensor 1 failed to retrieve data,default values set to 0. Retrying...")
        print("|  Fans remains unchanged...")
    #------------------------------END OF TRY 1 ----------------------------
    print("|                        --------------------------                         ")
    #--------------------------Try Catch for sensor 2----------------------------      
    try:
        temperature2 = dht22_2.temperature
        humidity2 = dht22_2.humidity
        print("|  Temp2: {:.1f}C*    Humid2: {}%".format(temperature2,humidity2))
        
        temp2 = int(temperature2)
        hum2 = int(humidity2)
        
        if(temp2 is None):
            continue
            print("|  No reading receivied, fans will remain as is.  ")

        if(temp2 >= 46):
            fanOn2()
#             fanOn3()
            
        if(temp2 < 46):
            fanOff2()
#             fanOff3()
            
    except RuntimeError as error:
        temp2 = 0
        hum2 = 0
        print("|  Sensor 2 failed to retrieve data,default values set to 0.  Retrying...")
        print("|  Fans remains unchanged...")
    print("|                        --------------------------                         ")
    interval = endTime - startTime    
    timeConvert(interval)
    
    #-------------------------END OF TRY NR 2--------------------------------
    
    #-----------------------DATABASE CONNECTION ADN CODE-------------------------
    #Variables for DB.
    
    dateDB = time.strftime("%Y-%m-%d")
    timeDB = now.strftime("%H:%M:%S")
    temp1DB = temp1
    hum1DB = hum1
    temp2DB = temp2
    hum2DB = hum2
    fanStat = getStat(temp2)
    timerDB = timeDBConvert(interval)
    
    try:
        con = mariadb.connect(
            user="user",
            passwd="pswd",
            host="host",
            port="port",
            database="db",
            )
        
    except mariadb.Error as e:
            print(f"Error connecting to mariaDB Platform: {e}")
            sys.exit(1)
    
    cur = con.cursor()

    try:
        cur.execute("INSERT INTO oven1 (temp_1, humid_1, temp_2, humid_2, fan_status) VALUES (%d, %d, %d, %d, %s)",
                (temp1DB, hum1DB, temp2DB, hum2DB, fanStat))
        con.commit()
        print("|  Record is inserted...")
    except:
        print("|  Something went wrong, no record has been inserted...")
        
    print("----------------------------------------------------------------------------")
    print("")
    print("")
    
    #Sleep timer.  
    time.sleep(360)
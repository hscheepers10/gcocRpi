from board import *
import RPi.GPIO as GPIO

def clean():
    relPin_1 = 20
    relPin_2 = 21
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relPin_1, GPIO.OUT)
    GPIO.setup(relPin_2, GPIO.OUT)

    GPIO.cleanup()

    print("=======================================")
    print("=======================================")
    print("===============CLEANED!!===============")
    print("=======================================")
    print("=======================================")
    
clean()
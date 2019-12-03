import RPi.GPIO as GPIO
import time 

RELAIS_1_GPIO = 21
GPIO.setmode(GPIO.BCM) # GPIO Nummern statt Board Nummern
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Modus zuweisen

try:
    while True:
        
        GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) 
        time.sleep(10)
        GPIO.output(RELAIS_1_GPIO, GPIO.LOW) 
        time.sleep(2)
except KeyboardInterrupt: 
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW) 
    GPIO.cleanup() 
    print('testus')
except:
    print('an error occured')
#finally:   
    #GPIO.output(RELAIS_1_GPIO, GPIO.LOW) 
    #GPIO.cleanup() 
    #print('an error occured')
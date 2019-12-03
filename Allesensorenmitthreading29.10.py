
import time
import sys
import urllib.request
import threading
import RPi.GPIO as GPIO
#lightsensor
import statistics

#für MCP3008
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from numpy import interp

#co2mhz19
import serial
import subprocess
import traceback

#dht_11
import Adafruit_DHT


#Hardware SPI configuration: ##das ist allgemein für MCP3008
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#co2sensor
partial_serial_dev = 'serial0'

serial_dev = '/dev/%s' % partial_serial_dev
stop_getty = 'sudo systemctl stop serial-getty@%s.service' % partial_serial_dev
start_getty = 'sudo systemctl start serial-getty@%s.service' % partial_serial_dev

#relais
RELAIS_1_GPIO = 21
GPIO.setmode(GPIO.BCM) # GPIO Nummern statt Board Nummern
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Modus zuweisen





def connect_serial():
  return serial.Serial(serial_dev,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1.0)
    




class dht_11:     #self-keyword anwenden allgemein bei classes
  humidity, temperature = Adafruit_DHT.read_retry(11, 4)

  def newmeasurments(self): ##that is a method, it belongs to the function object.
    while True:
      self.temperature=Adafruit_DHT.read_retry(11, 4)[1]
      self.humidity=Adafruit_DHT.read_retry(11, 4)[0]
      time.sleep(2)

class lightsensors:
  values = [0]*8
  zette=[100]
  def medianlight(self):
    while True:
      locklight.acquire()
      try:
        self.data=[]
        for i in range(5):      
            for i in range(8):
                  # The read_adc function will get the value of the specified channel (0-7).
                self.values[i] = mcp.read_adc(i)
            for i in range(2):          #menge an sensoren
                self.data.append(self.values[i])
            time.sleep(0.5)
        # Print the ADC values.
        self.data=statistics.mean(self.data)
        self.data=round(interp(self.data, [0, 1023], [0, 100]),2)
        lightsensors.zette=self.data
      finally:
        locklight.release()
      
      time.sleep(2)

class mh_z19:
  co2level={}
  co2levelfloat=[]
  def werte(self):
    while True:
      lockco2.acquire()
      p = subprocess.call(stop_getty, stdout=subprocess.PIPE, shell=True)
      try:
        ser = connect_serial()
        while 1:
          result=ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
          s=ser.read(9)
          if len(s) >= 4 and s[0] == 0xff and s[1] == 0x86:
            self.co2level= {'co2': s[2]*256 + s[3]}
            self.co2levelfloat=[s[2]*256 + s[3]]
            break
      except:
        traceback.print_exc()
      
      finally:
        lockco2.release()
        p = subprocess.call(start_getty, stdout=subprocess.PIPE, shell=True)
      
      time.sleep(2)

def relais():
  lichtsensor=lightsensors()
  while True:
    locklight.acquire()
    print('last time printing this'+str(lichtsensor.zette))
   # print('testing whaterver:'+str(lichtsensor.data[0]))
    if lichtsensor.zette <= 18:
      locklight.release()
      GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) 
      time.sleep(10)
      GPIO.output(RELAIS_1_GPIO, GPIO.LOW) 
    else:
      locklight.release()
      time.sleep(10)
        
      
        


sensor=dht_11()
lichtsensor=lightsensors()
co2sensor=mh_z19()

#locks
locklight=threading.Lock()
lockco2=threading.Lock()


a=threading.Thread(name='humidity, temperature', target=sensor.newmeasurments, daemon=True)
b=threading.Thread(name='light', target=lichtsensor.medianlight, daemon=True)
c=threading.Thread(name='co2', target=co2sensor.werte, daemon=True)
d=threading.Thread(name='relais', target=relais, daemon=True)
a.start()
b.start()
c.start()
d.start()



while True:
  try:
      print(sensor.temperature)
      print(sensor.humidity)
      #licht
      locklight.acquire()
      lockco2.acquire()
      try:
        print(lichtsensor.data)
        print('das ist wohl'+str(lichtsensor.zette))
        print('das ist die'+str(lichtsensor.data))
       
        print(co2sensor.co2level)
      finally:
        locklight.release()
        lockco2.release()
      time.sleep(5)
  except KeyboardInterrupt: 
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW) 
    GPIO.cleanup() 
    print('testus')
    sys.exit()
 

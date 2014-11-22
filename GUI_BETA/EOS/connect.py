import serial,threading
from time import sleep

CONNECTED = b"\x01"
UI = b"\x02"
GUI = b"\x01"
EX_SETUP = b"\x03"
SETPOINT = b"\x00"
PRE_SETPOINT = b"\x01"
ABORT = b"\x04"
RUN = b"\x05"

class Connection():
    
    def __init__(self, port1):
        self.ser = serial.Serial(
                    port=port1,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)
    
    def sendText(self,text,queue):
        def callback():
            # send the character to the device
            self.ser.write(text.encode())
            out = ''
            sleep(.3)
            while self.ser.inWaiting() > 0:
                out += self.ser.read().decode()
            queue.put(out)
        t = threading.Thread(target=callback)
        t.start()
        
    def sendByte(self,byte,queue):
        def callback():
            # send the character to the device
            self.ser.write(byte)
            sleep(.3)
            while self.ser.inWaiting() > 0:
                out = self.ser.read()
            queue.put(out)
        t = threading.Thread(target=callback)
        t.start()
    
    def getPort(self):
        return self.ser.portstr
    
    def closePort(self):
        self.ser.close()
    
    def initStepExperiment(self,currentExp):
        def callback():
            self.ser.write(UI)
            self.ser.write(GUI)
            self.ser.write(EX_SETUP)
            self.ser.write(SETPOINT)
            self.ser.write(currentExp["minTemp"].encode())
            self.ser.write(currentExp["maxTemp"].encode())
            self.ser.write(currentExp["intervals"].encode())
            self.ser.write(currentExp["time"].encode())
        t = threading.Thread(target=callback)
        t.start()

    def initPreSetExperiment(self,currentExp):
        def callback():
            self.ser.write(UI)
            self.ser.write(GUI)
            self.ser.write(EX_SETUP)
            self.ser.write(PRE_SETPOINT)
            setpoints = currentExp["setPoints"]
            self.ser.write(len(setpoints))
            for setpoint in setpoints:
                self.ser.write(setpoint)
            self.ser.write(currentExp[""].encode())
            self.ser.write(currentExp["time"].encode())
        t = threading.Thread(target=callback)
        t.start()
    
    def updater(self, queue):
        def callback():
            if self.ser.inWaiting() > 0:
                queue.put(self.ser.read())
            sleep(1)
            callback()
        t = threading.Thread(target=callback)
        t.start()
    
import serial,threading
from time import sleep

class Connection():
    
    def __init__(self, port1):
        self.ser = serial.Serial(
                    port=port1,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)
        self.CONNECTED = b"\x01"
        self.UI = b"\x02"
        self.GUI = b"\x01"
        self.EX_SETUP = b"\x03"
        self.SETPOINT = b"\x00"
        self.PRE_SETPOINT = b"\x01"
        self.ABORT = b"\x04"
        self.RUN = b"\x05"
    
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
        
    def sendByte(self,byte):
        def callback():
            self.ser.write(byte)
        t = threading.Thread(target=callback)
        t.start()
    
    def sendByteTwoWay(self,byte,queue):
        def callback():
            # send the character to the device
            self.ser.write(byte)
            sleep(.3)
            out = None
            while self.ser.inWaiting() > 0:
                out = self.ser.read()
            queue.put(out)
        t = threading.Thread(target=callback)
        t.start()
        
    def initUI(self):
        def callback():
            self.ser.write(self.CONNECTED)
            self.ser.write(self.UI)
            self.ser.write(self.GUI)
        t = threading.Thread(target=callback)
        t.start()
    
    def getPort(self):
        return self.ser.portstr
    
    def closePort(self):
        self.ser.close()
    
    def initStepExperiment(self,currentExp):
        def callback():
            self.ser.write(self.EX_SETUP)
            self.ser.write(self.SETPOINT)
            self.ser.write(bytes( [ int(currentExp["minTemp"])] ) )
            self.ser.write(bytes( [ int(currentExp["maxTemp"]) ]))
            self.ser.write(bytes( [int(currentExp["intervals"])]))
            self.ser.write(bytes( [ int(currentExp["time"]) ]))
            self.ser.write(self.RUN)
        t = threading.Thread(target=callback)
        t.start()

    def initPreSetExperiment(self,currentExp):
        def callback():
            self.ser.write(self.EX_SETUP)
            self.ser.write(self.PRE_SETPOINT)
            setpoints = currentExp["setPoints"]
            self.ser.write(len(setpoints))
            for setpoint in setpoints:
                self.ser.write(setpoint)
            self.ser.write(currentExp[""].encode())
            self.ser.write(currentExp["time"].encode())
        t = threading.Thread(target=callback)
        t.start()
    
    def updater(self, queue,parent):
        def callback():
            if self.ser.inWaiting() > 0:
                queue.put(self.ser.read())
            parent.after(200,callback)
            #sleep(.1)
            #callback()
        t = threading.Thread(target=callback)
        t.start()
    
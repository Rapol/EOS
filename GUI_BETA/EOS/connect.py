import serial,threading,sched,time
from sched import scheduler

class Connection():
    
    def __init__(self, port1, queue):
        try:
            self.ser = serial.Serial(
                    port=port1,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=2)
        except:
            print("Error creating Port")
            return
        self.CONNECTED = b"\x01"
        self.UI = b"\x02"
        self.GUI = b"\x01"
        self.EX_SETUP = b"\x03"
        self.SETPOINT = b"\x00"
        self.PRE_SETPOINT = b"\x01"
        self.ABORT = b"\x04"
        self.RUN = b"\x05"
        
        self.queue = queue
        
        self.scheduler = None
        self.event = None
    
    def sendText(self,text):
        def callback():
            # send the character to the device
            self.ser.write(text.encode())
            out = ''
            time.sleep(.3)
            while self.ser.inWaiting() > 0:
                out += self.ser.read().decode()
            self.queue.put(out)
        t = threading.Thread(target=callback)
        t.start()
        
    def sendByte(self,byte):
        def callback():
            self.ser.write(byte)
        t = threading.Thread(target=callback)
        t.start()
    
    def sendByteTwoWay(self,byte):
        def callback():
            # send the character to the device
            self.ser.write(byte)
            time.sleep(.3)
            out = None
            while self.ser.inWaiting() > 0:
                out = self.ser.read()
            self.queue.put(out)
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
        self.ser.flushInput()
        t = threading.Thread(target=callback)
        t.start()

    def initPreSetExperiment(self,currentExp):
        def callback():
            self.ser.write(self.EX_SETUP)
            self.ser.write(self.PRE_SETPOINT)
            setpoints = currentExp["setPoints"]
            print(len(setpoints))
            self.ser.write(bytes( [ int(len(setpoints))] ))
            for setpoint in setpoints:
                self.ser.write(bytes( [ int(setpoint)] ))
            self.ser.write(bytes( [ int( currentExp["time"] )] ))
            self.ser.write(self.RUN)
        self.ser.flushInput()
        t = threading.Thread(target=callback)
        t.start()
        
    def updater(self):
        def callback(scheduler=None):
            if scheduler is None:
                scheduler = sched.scheduler(time.time, time.sleep)
                scheduler.enter(0,1,callback,([scheduler]))
                scheduler.run()
            scheduler.enter(.1,1,callback,([scheduler]))
            if self.ser.inWaiting() > 0:
                a = self.ser.read()
                self.queue.put(a)
        t = threading.Thread(target=callback)
        t.start()
        
#     def stopUpdater(self):
#         try:
#             self.scheduler.cancel(self.event)
#         except:
#             print("No event found in queue")
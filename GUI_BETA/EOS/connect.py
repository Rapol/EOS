import serial,time


class Connection():
    
    def __init__(self, port1):
        self.ser = serial.Serial(
                    port=port1,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)
    
    def sendText(self,text):
        if text == 'exit':
            self.ser.close()
            exit()
        else:
            # send the character to the device
            self.ser.write(text.encode())
            out = ''
            time.sleep(.3)
            while self.ser.inWaiting() > 0:
                out += self.ser.read().decode()
            return out
    
    def getPort(self):
        return self.ser.portstr
    
    def closePort(self):
        self.ser.close()
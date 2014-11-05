import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import java.util.TooManyListenersException;

import gnu.io.*;

public class TwoWaySerialComm implements SerialPortEventListener{

	InputStream in;
	OutputStream out;

	public void connect(CommPortIdentifier portIdentifier) {
		try {
			// Open serial port
			int timeout = 2000;
			SerialPort commPort = (SerialPort) portIdentifier.open("SerialComm", timeout);
			// Set serial params
			commPort.setSerialPortParams(19200, SerialPort.DATABITS_8, SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
			
			// Get input and output stream
			in = commPort.getInputStream();
			out = commPort.getOutputStream();
			
			// Add listener to the port
			commPort.addEventListener(this);
			commPort.notifyOnDataAvailable(true);
			
		} catch (PortInUseException | UnsupportedCommOperationException | IOException | TooManyListenersException e) {
			System.out.println(e);
		}
	}
	
	public void serialEvent(SerialPortEvent event) {
		switch (event.getEventType()) {
		case SerialPortEvent.BI:
		case SerialPortEvent.OE:
		case SerialPortEvent.FE:
		case SerialPortEvent.PE:
		case SerialPortEvent.CD:
		case SerialPortEvent.CTS:
		case SerialPortEvent.DSR:
		case SerialPortEvent.RI:
		case SerialPortEvent.OUTPUT_BUFFER_EMPTY:
			break;
		case SerialPortEvent.DATA_AVAILABLE:
			// Data is 1 byte length
			byte[] buffer = new byte[1];
			int len = -1;
			try {
				// Read if inputStream has data
				while ((len = this.in.read(buffer)) > -1) {
					// Output to console
					System.out.print(new String(buffer, 0, len));
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
			break;
		}
	}
	
	public void writeToConsole(String s){
		try {
			out.write(s.getBytes());
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
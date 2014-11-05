import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import java.util.TooManyListenersException;

import gnu.io.*;

public class TwoWaySerialComm implements SerialPortEventListener{

	InputStream in;
	
	public static void main(String[] args) {
		try {
			TwoWaySerialComm tiva = new TwoWaySerialComm();
			Enumeration portList = CommPortIdentifier.getPortIdentifiers();
			// Iterate through the ports
			while (CommPortIdentifier.getPortIdentifiers().hasMoreElements()) {
				CommPortIdentifier portId = (CommPortIdentifier) portList.nextElement();
				// Find serial port COM8
				if (portId.getPortType() == CommPortIdentifier.PORT_SERIAL) {
					if (portId.getName().equals("COM8")) {
						tiva.connect(portId);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	void connect(CommPortIdentifier portIdentifier) {
		try {
			// Open serial port
			int timeout = 2000;
			SerialPort commPort = (SerialPort) portIdentifier.open("SerialComm", timeout);
			// Set serial params
			commPort.setSerialPortParams(19200, SerialPort.DATABITS_8, SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
			
			// Get input and output stream
			in = commPort.getInputStream();
			OutputStream out = commPort.getOutputStream();
			
			// Add listener to the port
			commPort.addEventListener(this);
			commPort.notifyOnDataAvailable(true);

			// Separate thread for output
			(new Thread(new SerialWriter(out))).start();
			
			// Testing SerialWriter
			String a = "hello this\nis dog";
			while (true) {
				out.write(a.getBytes());
				Thread.sleep(2000);
			}
			
		} catch (PortInUseException | UnsupportedCommOperationException | IOException | InterruptedException | TooManyListenersException e) {
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

	public static class SerialWriter implements Runnable {

		OutputStream out;

		public SerialWriter(OutputStream out) {
			this.out = out;
		}

		public void run() {
			try {
				int c = 0;
				while ((c = System.in.read()) > -1) {
					this.out.write(c);
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

}
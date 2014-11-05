import gnu.io.CommPortIdentifier;

import java.awt.*;

import javax.swing.*;

import java.awt.event.*;
import java.util.Enumeration;

public class Console extends JFrame implements ActionListener
{
	private static final int WIDTH = 400;
	private static final int HEIGHT = 300;
	
	private JTextField outputTF;
	private JLabel outputL, inputL;
	static JTextArea inputTA;
	
	public static void main(String[] args)
	{
		Console gui = new Console();
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
	
	public Console ()
	{	
		outputL = new JLabel("Output: ");
		inputL = new JLabel("Input: ");
		outputTF = new JTextField(20);
		outputTF.addActionListener(this);
		
		inputTA = new JTextArea(10, 10);
		JScrollPane scrollPane = new JScrollPane(inputTA); 
		inputTA.setEditable(false);
		
		setTitle("Console");
		Container pane = getContentPane();
		pane.setLayout(new GridLayout(4,1));
		
		//Add things to the pane in the order you want them to appear (left to right, top to bottom)
		pane.add(outputL);
		pane.add(outputTF);
		pane.add(inputL);
		pane.add(scrollPane);
		
		setSize(WIDTH, HEIGHT);
		setVisible(true);
		setDefaultCloseOperation(EXIT_ON_CLOSE);
	}
	
	public void actionPerformed(ActionEvent evt) {
	      // Get the String entered into the TextField tfInput, convert to int
	      String textIn = outputTF.getText();
	      outputTF.setText("");
	      inputTA.append(textIn + "\n");
	   }
	
}

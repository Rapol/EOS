/*
 * lcd.c
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <inc/tm4c123gh6pm.h>
#include "inc/hw_memmap.h"
#include "inc/hw_types.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/debug.h"
#include "driverlib/fpu.h"
#include "driverlib/pin_map.h"
#include "driverlib/rom.h"
#include "lcd.h"

// LCD Pins
// PC4 => D4
// PC5 => D5
// PC6 => D6
// PC7 => D7
// PA6 => RS
// PA7 => E

void LCD_Write(unsigned char inputData) {

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, (inputData & 0xf0));
	GPIOPinWrite(LCD_COMMAND_PORT, RS, RS);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((100e-6) * CLKSPEED / 3);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, (inputData & 0x0f) << 4);
	GPIOPinWrite(LCD_COMMAND_PORT, RS, RS);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((5e-3) * CLKSPEED / 3);

}

void LCD_WriteText(char* inputText, unsigned char row, unsigned char col) {
	unsigned char address_d = 0;		// address of the data in the screen.
	switch (row) {
	case 0:
		address_d = 0x80 + col;		// at zeroth row
		break;
	case 1:
		address_d = 0xC0 + col;		// at first row
		break;
	case 2:
		address_d = 0x94 + col;		// at second row
		break;
	case 3:
		address_d = 0xD4 + col;		// at third row
		break;
	default:
		address_d = 0x80 + col;	// returns to first row if invalid row number is detected
		break;
	}

	LCD_Command(address_d);

	while (*inputText)					// Place a string, letter by letter.
		LCD_Write(*inputText++);
}

void LCD_Command(unsigned char command) {

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, (command & 0xf0));
	GPIOPinWrite(LCD_COMMAND_PORT, RS, 0x00);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((100e-6) * CLKSPEED / 3);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, (command & 0x0f) << 4);
	GPIOPinWrite(LCD_COMMAND_PORT, RS, 0x00);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((5e-3) * CLKSPEED / 3);

}

void LCD_Init(void) {

	GPIOPinTypeGPIOOutput(LCD_DATA_PORT, D4 | D5 | D6 | D7);
	GPIOPinTypeGPIOOutput(LCD_COMMAND_PORT, RS | E);

	// Please refer to the HD44780 datasheet for how these initializations work!
	SysCtlDelay((500e-3) * CLKSPEED / 3);

	GPIOPinWrite(LCD_COMMAND_PORT, RS, 0x00);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, 0x30);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((50e-3) * CLKSPEED / 3);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, 0x30);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((50e-3) * CLKSPEED / 3);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, 0x30);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((10e-3) * CLKSPEED / 3);

	GPIOPinWrite(LCD_DATA_PORT, D4 | D5 | D6 | D7, 0x20);
	GPIOPinWrite(LCD_COMMAND_PORT, E, E);
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIOPinWrite(LCD_COMMAND_PORT, E, 0x00);

	SysCtlDelay((10e-3) * CLKSPEED / 3);

	LCD_Command(0x01);	// Clear the screen.
	LCD_Command(0x06);	// Cursor moves right.
	LCD_Command(0x0f);	// Cursor blinking, turn on LCD.
}

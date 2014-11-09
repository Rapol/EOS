/*
 * lcd.c
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega
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

// Enable toggle to send data
void LCD_ToggleEnable(void) {
	GPIO_PORTA_DATA_R ^= 0x80;
	SysCtlDelay((20e-6) * CLKSPEED / 3);
	GPIO_PORTA_DATA_R ^= 0x80;
	//Wait time > 41ms
	SysCtlDelay((50e-3) * CLKSPEED / 3);
}

void LCD_MoveCursor(int displayLine) {
	// Setting obligatory one
	displayLine |= 0x80;
	// RS clear
	GPIO_PORTA_DATA_R &= ~0x40;
	// Set address
	GPIO_PORTC_DATA_R = displayLine;
	LCD_ToggleEnable();
	GPIO_PORTC_DATA_R = displayLine << 4;
	LCD_ToggleEnable();
}

// Clear screen and reset cursor to the first line
void LCD_ClearScreen(void) {
	// Clear RS
	GPIO_PORTA_DATA_R &= ~0x40;
	// Clear display        0 0 | 0 0 0 0 0 0 0 1
	GPIO_PORTC_DATA_R = 0x00;
	LCD_ToggleEnable();
	GPIO_PORTC_DATA_R = 0x10;
	LCD_ToggleEnable();

	// Move Cursor to first line
	LCD_MoveCursor(FIRST_LINE);
}

void LCD_Init(void) {
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOC);

	// Initializing PortA
	GPIO_PORTA_CR_R = 0xC0;                 // allow changes to PA6 and PA7
	GPIO_PORTA_PCTL_R &= ~0xFF000000;       // GPIO clear bit PCTL
	GPIO_PORTA_DIR_R |= 0xC0;               // PA6 and PA7 outputs
	GPIO_PORTA_AFSEL_R &= ~0xC0;            // not alternative
	GPIO_PORTA_AMSEL_R &= ~0xC0;            // no analog
	GPIO_PORTA_DEN_R |= 0xC0;               // enable PAs

	// Initializing PortC
	GPIO_PORTC_CR_R = 0xF0;                 // allow changes to PC4 => PC7
	GPIO_PORTC_PCTL_R &= ~0xFFFF0000;       // GPIO clear bit PCTL
	GPIO_PORTC_DIR_R |= 0xF0;               // PC4 => PC7 outputs
	GPIO_PORTC_AFSEL_R &= ~0xF0;            // not alternative
	GPIO_PORTC_AMSEL_R &= ~0xF0;            // no analog
	GPIO_PORTC_DEN_R |= 0xF0;               // enable PCs

	// Clear pins
	GPIO_PORTC_DATA_R = 0x00;
	GPIO_PORTA_DATA_R = 0x00;

	// Wait for LCD to stabilize
	//Wait time > 15ms
	SysCtlDelay((500e-3) * CLKSPEED / 3);

	// Clear RS for instructions
	GPIO_PORTA_DATA_R &= ~0x40;

	// Sets 4bit operation  0 0 | 0 0 1 0
	GPIO_PORTC_DATA_R = 0x20;
	LCD_ToggleEnable();

	// Select line display  0 0 | 0 0 1 0 1 0 * *
	GPIO_PORTC_DATA_R = 0x20;
	LCD_ToggleEnable();
	GPIO_PORTC_DATA_R = 0x80;
	LCD_ToggleEnable();

	// Turn on display      0 0 | 0 0 0 0 1 1 1 1
	GPIO_PORTC_DATA_R = 0x00;
	LCD_ToggleEnable();
	GPIO_PORTC_DATA_R = 0xF0;
	LCD_ToggleEnable();

	// Entry mode set       0 0 | 0 0 0 0 0 1 1 0
	GPIO_PORTC_DATA_R = 0x00;
	LCD_ToggleEnable();
	GPIO_PORTC_DATA_R = 0x60;
	LCD_ToggleEnable();

	LCD_ClearScreen();
}

// Send chars of the string
void LCD_SendChars(char *init) {
	// Loop until null character
	GPIO_PORTA_DATA_R |= 0x40;
	//Wait time > 41ms
	SysCtlDelay((50e-3) * CLKSPEED / 3);
	while (*init) {
		// Send the 4 most significant bits of the char
		GPIO_PORTC_DATA_R = *init;
		LCD_ToggleEnable();
		// Send the 4 least significant bits of the char
		GPIO_PORTC_DATA_R = *init << 4;
		LCD_ToggleEnable();
		// Change pointer to the next char
		*init++;
	}
}

/*
 * uart.c
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
#include "driverlib/uart.h"
#include "utils/uartstdio.h"
#include "uart.h"

// UART pins
// PB0 => U1Rx (Bluetooth) (USB)
// PB1 => U1Tx (Bluetooth) (USB)

//
// Setup UARTs
//
void UART_Init(void) {
	// Enable the GPIO Peripheral used by the UARTs.
//	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
	// Enable UART0
	SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
	// Enable UART1
	SysCtlPeripheralEnable(SYSCTL_PERIPH_UART1);

	// Configure GPIO pins for UART0
	GPIOPinConfigure(GPIO_PA0_U0RX);
	GPIOPinConfigure(GPIO_PA1_U0TX);
	GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
	// Configure GPIO pins for UART1
	GPIOPinConfigure(GPIO_PB0_U1RX);
	GPIOPinConfigure(GPIO_PB1_U1TX);
	GPIOPinTypeUART(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1);

	// Enable debug console on UART0 at 115200 baud
	UARTClockSourceSet(UART0_BASE, UART_CLOCK_PIOSC);
	UARTConfigSetExpClk(UART0_BASE, 16000000, 9600,
	        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
	// Setup UART1 at 9600 baud
	UARTClockSourceSet(UART1_BASE, UART_CLOCK_PIOSC);
	UARTConfigSetExpClk(UART1_BASE, 16000000, 9600,
			(UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
	// Enable RTS/CTS HW flow control for UART1
	UARTFlowControlSet(UART1_BASE, UART_FLOWCONTROL_RX | UART_FLOWCONTROL_TX);

	UARTEnable(UART0_BASE);
	// Enable UART1, this call also enables the FIFO buffer necessary for HW flow control
	UARTEnable(UART1_BASE);

	IntEnable(INT_UART0); //enable the UART interrupt
	IntEnable(INT_UART1); //enable the UART interrupt
	UARTIntEnable(UART0_BASE, UART_INT_RX | UART_INT_RT); //only enable RX and TX interrupts
	UARTIntEnable(UART1_BASE, UART_INT_RX | UART_INT_RT); //only enable RX and TX interrupts
}

//
// Prints a string (buf)
//
void UART_Printf(uint32_t uart_base, const char *buf) {
	while (*buf) {
		UARTCharPut(uart_base, *buf++);
	}
}

//
// Prints a string (buf) followed by a CRLF (\r\n)
//
void UART_Println(uint32_t uart_base, const char *buf) {
	while (*buf) {
		UARTCharPut(uart_base, *buf++);
	}
	UARTCharPut(uart_base, '\r');
	UARTCharPut(uart_base, '\n');
}

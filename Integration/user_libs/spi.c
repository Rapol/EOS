/*
 * spi.c
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Daniel Navarro
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
#include "driverlib/ssi.h"
#include "spi.h"

// SPI Pins
// PB4 => clock
// PB6 => RX
// PB7 => TX
// PE5 => CS

void SPI_Init(void) {
	//
	// Initialize the 3 pins we will need for SPI communication with the Potentiometer
	//
	SysCtlPeripheralEnable(SYSCTL_PERIPH_SSI2);
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
	// connect CS to pin E5
	GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_5);
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, 0);
	// Connect SPI to PB4 (clock), PB6 (RX) and PB7(TX)
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
	GPIOPinConfigure(GPIO_PB4_SSI2CLK);
	GPIOPinConfigure(GPIO_PB7_SSI2TX);
	GPIOPinConfigure(GPIO_PB6_SSI2RX);
	GPIOPinTypeSSI(GPIO_PORTB_BASE, GPIO_PIN_4 | GPIO_PIN_7 | GPIO_PIN_6);

	//
	// Configure SSI2
	//
	SSIConfigSetExpClk(SSI2_BASE, SysCtlClockGet(), SSI_FRF_MOTO_MODE_0,
	SSI_MODE_MASTER, 10000000, 16);

	//
	// Enable the SSI module.
	//
	SSIEnable(SSI2_BASE);
}

void SPI_WriteToPotentiometer(uint16_t command, uint16_t data) {
	uint16_t spidata;

	spidata = command << 8;
	spidata = spidata | data;

	SSIDataPut(SSI2_BASE, spidata);
	//
	// Wait until SSI is done transferring all the data in the transmit FIFO
	//
	while (SSIBusy(SSI2_BASE))
		;

	//
	// Hit the SSI latch, locking in the data
	//
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, GPIO_PIN_5);
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, 0);
}

uint32_t SPI_ReadTemperature(void) {
	uint32_t pui32DataRx[NUM_SSI_DATA];
	uint32_t ui32Index;

	// Read any residual data from the SSI port.  This makes sure the receive
	while (SSIDataGetNonBlocking(SSI2_BASE, &pui32DataRx[0]))
		;

	// Send dummy data - MAJIK
	SSIDataPut(SSI2_BASE, 0x00);
	while (SSIBusy(SSI2_BASE))
		;
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, GPIO_PIN_5);
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, 0);
	SSIDataPut(SSI2_BASE, 0x00);
	while (SSIBusy(SSI2_BASE))
		;
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, GPIO_PIN_5);
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, 0);

	//
	// Receive 4 bytes (2x16 bit) of data.
	//
	for (ui32Index = 0; ui32Index < NUM_SSI_DATA; ui32Index++) {
		// Receive the data
		SSIDataGet(SSI2_BASE, &pui32DataRx[ui32Index]);
	}

	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, GPIO_PIN_5);
	GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_5, 0);

	// Shift right 2 bits.
	pui32DataRx[0] >>= 2;

	return (pui32DataRx[0]);
}

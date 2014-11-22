/*
 * spi.h
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#ifndef SPI_H_
#define SPI_H_

// SPI Pins
// PB4 => clock
// PB6 => RX
// PB7 => TX
// PE5 => CS

#define NUM_SSI_DATA	2

extern void SPI_Init(void);
extern void SPI_WriteToPotentiometer(uint16_t command, uint16_t data);
extern uint32_t SPI_ReadTemperature(void);

#endif /* SPI_H_ */

/*
 * uart.h
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda
 */

#ifndef UART_H_
#define UART_H_

// UART pins
// PB0 => U1Rx (Bluetooth) (USB)
// PB1 => U1Tx (Bluetooth) (USB)

extern void UART_Init(void);
extern void UART_Printf(uint32_t uart_base, const char *buf);
extern void UART_Println(uint32_t uart_base, const char *buf);

#endif /* UART_H_ */

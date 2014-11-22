/*
 * lcd.h
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#ifndef LCD_H_
#define LCD_H_

// Port Pins
// LCD
// PC4 => D4
// PC5 => D5
// PC6 => D6
// PC7 => D7
// PA6 => RS
// PA7 => E

//#define FIRST_LINE	0x00
//#define SECOND_LINE	0x40
//#define CLKSPEED	40000000
#define LCD_DATA_PORT	GPIO_PORTC_BASE
#define LCD_COMMAND_PORT	GPIO_PORTA_BASE
#define RS	GPIO_PIN_6
#define E	GPIO_PIN_7
#define D4	GPIO_PIN_4
#define D5	GPIO_PIN_5
#define D6	GPIO_PIN_6
#define D7	GPIO_PIN_7
#define CLKSPEED	40000000

extern void LCD_Init(void);
extern void LCD_Command(unsigned char command);
extern void LCD_Write(unsigned char inputData);
extern void LCD_WriteText(char* inputText, unsigned char row, unsigned char col);

#endif /* LCD_H_ */

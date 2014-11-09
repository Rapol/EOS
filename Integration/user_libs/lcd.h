/*
 * lcd.h
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega
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

#define FIRST_LINE	0x00
#define SECOND_LINE	0x40
#define CLKSPEED	40000000

extern void LCD_ToggleEnable(void);
extern void LCD_MoveCursor(int displayLine);
extern void LCD_ClearScreen(void);
extern void LCD_Init(void);
extern void LCD_SendChars(char *init);

#endif /* LCD_H_ */

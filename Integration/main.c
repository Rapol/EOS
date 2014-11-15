/*
 * main.c
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "math.h"

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
#include "driverlib/timer.h"
#include "driverlib/pwm.h"

#include "user_libs/adc.h"
#include "user_libs/lcd.h"
#include "user_libs/uart.h"
#include "user_libs/spi.h"
#include "user_libs/pwm.h"

//----------------------v Port Pins v----------------------

// LCD
// PC4 => D4
// PC5 => D5
// PC6 => D6
// PC7 => D7
// PA6 => RS
// PA7 => E

// ADC
// PE3 => ADC0 (Sample)
// PE2 => ADC1 (Reference)

// SPI
// PB4 => clock
// PB6 => RX
// PB7 => TX
// PE5 => CS

// UART
// PB0 => U1Rx (Bluetooth) (USB)
// PB1 => U1Tx (Bluetooth) (USB)

// PWM Pins
// PE4 => M0PWM4 (Fan)
// PB5 => M0PWM3 (TC)

// LEDs
// PA3 => Red
// PA4 => Blue

//----------------------^ Port Pins ^----------------------

#define RESISTANCE_RATIO 10	// 10Kohm/1Kohm
#define INTRO	"  ______ ____   _____                            \r\n |  ____/ __ \\ / ____|                           \r\n | |__ | |  | | (___                             \r\n |  __|| |  | |\\___ \\                            \r\n | |___| |__| |____) |                           \r\n |______\\____/|_____/              _             \r\n |  \\/  |                         (_)            \r\n | \\  / | ___  __ _ ___ _   _ _ __ _ _ __   __ _ \r\n | |\\/| |/ _ \\/ _` / __| | | | '__| | '_ \\ / _` |\r\n | |  | |  __/ (_| \\__ \\ |_| | |  | | | | | (_| |\r\n |_|__|_|\\___|\\__,_|___/\\__,_|_|  |_|_| |_|\\__, |\r\n  / ____|         | |                       __/ |\r\n | (___  _   _ ___| |_ ___ _ __ ___        |___/ \r\n  \\___ \\| | | / __| __/ _ \\ '_ ` _ \\             \r\n  ____) | |_| \\__ \\ ||  __/ | | | | |            \r\n |_____/ \\__, |___/\\__\\___|_| |_| |_|            \r\n          __/ |                                  \r\n         |___/                                   "
#define FAN	PWM_OUT_4
#define TC	PWM_OUT_3
#define RED_LED	GPIO_PIN_3
#define BLUE_LED	GPIO_PIN_4

// Global variables
int value = 0, command = 0x11, flag = 0, nop = 0;
float resistance_sample_real, resistance_sample_exp, resistance_pot = 0,
		voltage_sample, voltage_ref, offset, voltage_difference = 0,
		voltage_difference_old = 0, setpointTemp = 0;
double tempF = 0;
char buffer[32];

int pulse = 2, nyx = 0, experimentRunning = 0, experimentCooling = 0;
float setpointValues[256], setpoints = 0, setpointsDone = 0;

int hours = 0, minutes = 0, seconds = 0;

void GPIOPortAHandler(void) {
	GPIOIntClear(GPIO_PORTA_BASE, GPIO_PIN_2);
	flag = 1;
}

void Timer0IntHandler(void) {
	// Clear the timer interrupt
	TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
	seconds = (seconds + 1) % 60;
	if (!seconds) {
		minutes = (minutes + 1) % 60;
		if (!minutes) {
			hours++;
		}
	}
	if (experimentRunning) {
		LCD_WriteText("Experiment: Running", 0, 0);
		if (seconds >= 10 && minutes < 10)
			sprintf(buffer, "Time: %d:0%d:%d", hours, minutes, seconds);
		else if (seconds < 10 && minutes < 10)
			sprintf(buffer, "Time: %d:0%d:0%d", hours, minutes, seconds);
		else if (seconds < 10 && minutes >= 10)
			sprintf(buffer, "Time: %d:%d:0%d", hours, minutes, seconds);
		else
			sprintf(buffer, "Time: %d:%d:%d", hours, minutes, seconds);
		LCD_WriteText(buffer, 1, 0);
		sprintf(buffer, "Temperature: %.2f ", tempF);
		LCD_WriteText(buffer, 2, 0);
		float percent = setpointsDone / (setpoints * 2.0 - 1.0) * 100.0;
		sprintf(buffer, "Done %.2f %%", percent);
		LCD_WriteText(buffer, 3, 0);
	} else if (experimentCooling) {
		sprintf(buffer, "Time: %d s", seconds);
		LCD_WriteText(buffer, 2, 0);
	}
}

int pulseValueForTC(float setpoint) {
	if (setpoint <= 71)
		return (pulse = 2);
	else if (setpoint <= 73)
		return (pulse = 3);
	else if (setpoint <= 74)
		return (pulse = 5);
	else if (setpoint <= 78)
		return (pulse = 7);
	else if (setpoint <= 88)
		return (pulse = 9);
	else if (setpoint <= 92)
		return (pulse = 11);
	else if (setpoint <= 98)
		return (pulse = 13);
	else if (setpoint <= 104)
		return (pulse = 15);
	else if (setpoint <= 113)
		return (pulse = 17);
	else if (setpoint <= 125)
		return (pulse = 19);
	else if (setpoint <= 135)
		return (pulse = 21);
	else if (setpoint <= 150)
		return (pulse = 23);
	else
		return (pulse = 23);
}

void toggleLED(uint32_t LED) {
	if (LED == BLUE_LED) {
		GPIOPinWrite(GPIO_PORTA_BASE, RED_LED, 0); // Red OFF (No experiment running)
		GPIOPinWrite(GPIO_PORTA_BASE, BLUE_LED, BLUE_LED); // Blue ON (System waiting to run experiment)
	} else {
		GPIOPinWrite(GPIO_PORTA_BASE, RED_LED, RED_LED); // Red ON (Experiment running)
		GPIOPinWrite(GPIO_PORTA_BASE, BLUE_LED, 0);	// Blue OFF
	}
}

int main(void) {
	// Set the clocking to run directly from the crystal.
	SysCtlClockSet(
	SYSCTL_SYSDIV_4 | SYSCTL_USE_PLL | SYSCTL_XTAL_16MHZ | SYSCTL_OSC_MAIN);

	SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);

	// Initialize ports
	SPI_Init();
	ADC_Init();
	UART_Init();
	LCD_Init();
	PWM_Init();

	TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);

	uint32_t ui32Period = SysCtlClockGet(); // 1 sec
	TimerLoadSet(TIMER0_BASE, TIMER_A, ui32Period);

	IntEnable(INT_TIMER0A);
	TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

	GPIOPinTypeGPIOInput(GPIO_PORTA_BASE, GPIO_PIN_2);
	GPIOIntTypeSet(GPIO_PORTA_BASE, GPIO_PIN_2, GPIO_RISING_EDGE);
	IntEnable(INT_GPIOA);
	GPIOIntEnable(GPIO_PORTA_BASE, GPIO_PIN_2);
	GPIOIntClear(GPIO_PORTA_BASE, GPIO_PIN_2);

	IntMasterEnable();

	TimerEnable(TIMER0_BASE, TIMER_A);

	GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE, GPIO_PIN_3 | GPIO_PIN_4);
	toggleLED(BLUE_LED);

	UART_Println(UART1_BASE, "Enabling UART..."); // software reset
	UART_Println(UART1_BASE, "UART enabled.");
	UART_Println(UART1_BASE, INTRO);

	do {
		LCD_Command(0x01);	// Clear the screen.
		// Display to LCD
		LCD_WriteText("System Enabled", 0, 0);
		LCD_WriteText("Awaiting experiment", 2, 0);
		toggleLED(BLUE_LED);
		char create = '0';
		do {
			create = '0';
			UART_Println(UART1_BASE,
					"\r\nDo you want to run a new experiment? [y/n]");
			while (create != 'y' && create != 'n') {
				create = UARTCharGet(UART1_BASE);
			}
			if (create == 'n') {
				UART_Println(UART1_BASE, "Do you wish to exit? [y/n]");
				char exit = '0';
				while (exit != 'y' && exit != 'n') {
					exit = UARTCharGet(UART1_BASE);
				}
				if (exit == 'y') {
					return 0;
				}
			}
		} while (create != 'y');
		char timber = '0';
		do {
			timber = '0';
			setpoints = 0;
			UART_Printf(UART1_BASE,
					"\r\nEnter the amount of setpoints for this experiment: ");
			while (!setpoints) {
				setpoints = UARTCharGet(UART1_BASE);
			}
			float setpointValue = 0;
			UART_Println(UART1_BASE,
					"\r\nNOTE: Termperature values are interpreted in Fahrenheit");
			int i = 0;
			for (i = 0; i < setpoints; i++) {
				sprintf(buffer, "Enter value for setpoint #%d: ", (i + 1));
				UART_Printf(UART1_BASE, buffer);
				while (!setpointValue) {
					setpointValue = UARTCharGet(UART1_BASE);
				}
				sprintf(buffer, "%.1f", setpointValue);
				UART_Println(UART1_BASE, buffer);
				setpointValues[i] = setpointValue;
				setpointValue = 0;
			}
			UART_Println(UART1_BASE, "Are you sure about this? [y/n]");
			while (timber != 'y' && timber != 'n') {
				timber = UARTCharGet(UART1_BASE);
			}
			if (timber == 'n') {
				UART_Println(UART1_BASE, "Do you wish to exit? [y/n]");
				char exit = '0';
				while (exit != 'y' && exit != 'n') {
					exit = UARTCharGet(UART1_BASE);
				}
				if (exit == 'y') {
					return 0;
				}
			}
		} while (timber != 'y');

		LCD_Command(0x01);	// Clear the screen.
		toggleLED(RED_LED);
		int i = 0;
		int currentSetpoint = 0;
		int heatingDone = 0;
		UART_Println(UART1_BASE, "Temperature \t| Resistance");
		hours = minutes = seconds = 0;
		experimentRunning = 1;
		while (1) {
			tempF = 1.8 * (SPI_ReadTemperature() * 0.25) + 32;
//			UART_Println(UART1_BASE, buffer);
			if (!nyx && !heatingDone)
				PWM_SetPulse(TC,
						pulseValueForTC(setpointValues[currentSetpoint]));
			if (heatingDone)
				PWM_SetPulse(TC, 2);
			PWM_SetFanVelocity(tempF, setpointValues[currentSetpoint], FAN);
//			sprintf(buffer, "%.1f F \t %d:%d:%d \r", tempF, hours, minutes,
//					seconds);
//			UART_Printf(UART1_BASE, buffer);
			if (round(tempF) == setpointValues[currentSetpoint]) { //(roundf(tempF * 10.0) / 10.0)
				float currentTemp = setpointValues[currentSetpoint];
				if ((currentSetpoint + 1) == setpoints) {
					heatingDone = 1;
				}
				if ((currentSetpoint - 1) < 0 && heatingDone) { // We're done
					flag = 1;
				}
				if (!heatingDone)
					currentSetpoint++;
				else
					currentSetpoint--;
				for (i = 0; i <= 255; i++) {
					voltage_difference_old = voltage_difference;
					SPI_WriteToPotentiometer(command, i);
					resistance_pot = i * 390.625 + 146.1;
					voltage_difference = ADC_VoltageDifference(&voltage_sample,
							&voltage_ref);
					if (voltage_difference > voltage_difference_old
							&& voltage_difference_old != 0) {
						resistance_sample_exp = resistance_pot
								* RESISTANCE_RATIO;
						offset = (voltage_sample * resistance_pot)
								/ (VDD
										* (resistance_sample_exp
												- (voltage_sample
														* resistance_sample_exp)
														/ VDD));
						resistance_sample_real = resistance_sample_exp * offset;
						sprintf(buffer, "%.1f \t| %.1f", currentTemp,
								resistance_sample_real);
						UART_Println(UART1_BASE, buffer);
						setpointsDone++;
//						LCD_ClearScreen();
//						LCD_SendChars(buffer);
						break;
					}
				}
				nyx = 0;
				pulse = 0;
			}
			if (!(minutes % 2) && minutes) {
				nyx = 1;
				if (pulse == 23 && !heatingDone)
					pulse -= 2;
//				else if (pulse == 0 && heatingDone)
//					pulse += 2;
				if (!heatingDone)
					PWM_SetPulse(TC, (pulse += 2));
//				else
//					PWM_SetPulse(TC, (pulse -= 2));
			}
			if (flag) {
				break;
			}
		}
		heatingDone = 0;
		setpointsDone = 0;
		experimentRunning = 0;
		flag = 0;
		pulse = 2;
		nyx = 0;

		// Cooling Phase
		PWM_SetPulse(TC, 2);
		LCD_Command(0x01);	// Clear the screen.
		LCD_WriteText("Experiment: Cooling", 1, 0);
		experimentCooling = 1;
		seconds = 0;
		PWM_SetPulse(FAN, 23);
		while (seconds < 59)
			;
		experimentCooling = 0;
		PWM_SetPulse(FAN, 2);
	} while (1);

}

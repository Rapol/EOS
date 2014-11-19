/*
 * pwm.c
 *
 *  Created on: Nov 6, 2014
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
#include "driverlib/timer.h"
#include "pwm.h"
#include "driverlib/pwm.h"

// PWM Pins
// PE4 => M0PWM4 (Fan)

void PWM_Init(void) {
	volatile uint32_t ui32Load;
	volatile uint32_t ui32PWMClock;

	//PWM Prescaler
	SysCtlPWMClockSet(SYSCTL_PWMDIV_64);

	//PWM Peripheral Enable
	SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);

	//Configure PE4 & PB5 Pins as PWM
	GPIOPinConfigure(GPIO_PE4_M0PWM4);
	GPIOPinTypePWM(GPIO_PORTE_BASE, GPIO_PIN_4);
	GPIOPinConfigure(GPIO_PB5_M0PWM3);
	GPIOPinTypePWM(GPIO_PORTB_BASE, GPIO_PIN_5);
	
	//Frequency of the PWM Clock
	ui32PWMClock = SysCtlClockGet() / 64;

	//Counter (Top) for the Period = 24
	ui32Load = (ui32PWMClock / PWM_FREQUENCY) - 1;

	//Configure PWM Options
	//PWM_GEN_2 Covers M1PWM4 and M1PWM5
	PWMGenConfigure(PWM0_BASE, PWM_GEN_2, PWM_GEN_MODE_UP_DOWN);
	//PWM_GEN_1 Covers M1PWM2 and M1PWM3
	PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_UP_DOWN );

	//Set the Period (expressed in clock ticks)
	PWMGenPeriodSet(PWM0_BASE, PWM_GEN_2, ui32Load);
	PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, ui32Load);

	//Set PWM duty-50% (Period /2)
	PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, 0);
	PWMPulseWidthSet(PWM0_BASE, PWM_OUT_3, 0);

	// Enable the PWM generator
	PWMGenEnable(PWM0_BASE, PWM_GEN_2); //This Line damages the correct display of the LCD
	PWMGenEnable(PWM0_BASE, PWM_GEN_1);

	// Turn on the Output pins
	PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT, true);
	PWMOutputState(PWM0_BASE, PWM_OUT_3_BIT, true);
}

void PWM_SetPulse(uint32_t ui32PWMOut, int step) {
	PWMPulseWidthSet(PWM0_BASE, ui32PWMOut, step*2);
}

void PWM_SetFanVelocity(float currentTemp, float setpointTemp, uint32_t ui32PWMOut) {
	float tempDiff = currentTemp - setpointTemp;

	if (tempDiff < 4) {
		PWM_SetPulse(ui32PWMOut, 1);
	}
	else if ((tempDiff >= 4) && (tempDiff <= 7)) {
		PWM_SetPulse(ui32PWMOut, 391);
	}
	else if ((tempDiff >= 8) && (tempDiff <= 11)) {
		PWM_SetPulse(ui32PWMOut, 521);
	}
	else if ((tempDiff >= 12) && (tempDiff <= 15)) {
		PWM_SetPulse(ui32PWMOut, 651);
	}
	else if ((tempDiff >= 16) && (tempDiff <= 19)) {
		PWM_SetPulse(ui32PWMOut, 781);
	}
	else if ((tempDiff >= 20) && (tempDiff <= 23)) {
		PWM_SetPulse(ui32PWMOut, 912);
	}
	else if ((tempDiff >= 24) && (tempDiff <= 27)) {
		PWM_SetPulse(ui32PWMOut, 1042);
	}
	else if ((tempDiff >= 28) && (tempDiff <= 32)) {
		PWM_SetPulse(ui32PWMOut, 1172);
	}
	else if ((tempDiff >= 33) && (tempDiff <= 35)) {
		PWM_SetPulse(ui32PWMOut, 1302);
	}
	else {
		PWM_SetPulse(ui32PWMOut, 1561);
	}
}

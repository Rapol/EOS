/*
 * pwm.c
 *
 *  Created on: Nov 6, 2014
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

	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
	SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);

	//Configure PE4 Pin as PWM
	GPIOPinConfigure(GPIO_PE4_M0PWM4);
//	GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_4);
	GPIOPinTypePWM(GPIO_PORTE_BASE, GPIO_PIN_4);
	//Frequency of the PWM Clock
	ui32PWMClock = SysCtlClockGet() / 64;

	//Counter (Top) for the Period = 24
	ui32Load = (ui32PWMClock / PWM_FREQUENCY) - 1;

	//Configure PWM Options
	//PWM_GEN_2 Covers M1PWM4 and M1PWM5
	PWMGenConfigure(PWM0_BASE, PWM_GEN_2, PWM_GEN_MODE_UP_DOWN);

	//Set the Period (expressed in clock ticks)
	PWMGenPeriodSet(PWM0_BASE, PWM_GEN_2, ui32Load);

	//Set PWM duty-50% (Period /2)
	PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, 0);

	// Enable the PWM generator
	PWMGenEnable(PWM0_BASE, PWM_GEN_2); //This Line damages the correct display of the LCD

	// Turn on the Output pins
	PWMOutputState(PWM0_BASE, PWM_OUT_4_BIT, true);
}

void PWM_SetPulse(int pulse) {
	PWMPulseWidthSet(PWM0_BASE, PWM_OUT_4, pulse);
}

void PWM_SetFanVelocity(float currentTemp, float setpointTemp) {
	float tempDiff = currentTemp - setpointTemp;

	if (tempDiff < 0) {
//		tempDiff *= -1;
	}

	if (tempDiff < 10) {
		PWM_SetPulse(0);
	}
	else if ((tempDiff >= 10) && (tempDiff <= 13)) {
		PWM_SetPulse(6);
	}
	else if ((tempDiff >= 14) && (tempDiff <= 17)) {
		PWM_SetPulse(8);
	}
	else if ((tempDiff >= 18) && (tempDiff <= 21)) {
		PWM_SetPulse(10);
	}
	else if ((tempDiff >= 22) && (tempDiff <= 25)) {
		PWM_SetPulse(12);
	}
	else if ((tempDiff >= 26) && (tempDiff <= 28)) {
		PWM_SetPulse(14);
	}
	else if ((tempDiff >= 29) && (tempDiff <= 32)) {
		PWM_SetPulse(16);
	}
	else if ((tempDiff >= 29) && (tempDiff <= 32)) {
		PWM_SetPulse(18);
	}
	else if ((tempDiff >= 33) && (tempDiff <= 35)) {
		PWM_SetPulse(20);
	}
	else {
		PWM_SetPulse(22);
	}
}

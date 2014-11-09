/*
 * pwm.h
 *
 *  Created on: Nov 6, 2014
 *      Author: Luis de la Vega, Daniel Navarro
 */

#ifndef PWM_H_
#define PWM_H_

// PWM Pins
// PE4 => M0PWM4 (Fan)

#define PWM_FREQUENCY	25000

extern void PWM_Init(void);
extern void PWM_SetPulse(int pulse);
extern void PWM_SetFanVelocity(float currentTemp, float setpointTemp);

#endif /* PWM_H_ */

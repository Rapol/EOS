/*
 * pwm.h
 *
 *  Created on: Nov 6, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#ifndef PWM_H_
#define PWM_H_

// PWM Pins
// PE4 => M0PWM4 (Fan)

#define PWM_FREQUENCY	250

extern void PWM_Init(void);
extern void PWM_SetPulse(uint32_t ui32PWMOut, int step);
extern void PWM_SetFanVelocity(float currentTemp, float setpointTemp, uint32_t ui32PWMOut);

#endif /* PWM_H_ */

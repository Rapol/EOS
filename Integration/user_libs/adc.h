/*
 * adc.h
 *
 *  Created on: Nov 5, 2014
 *      Author: Luis de la Vega, Juan Miranda, Daniel Navarro, Rafael Pol
 */

#ifndef ADC_H_
#define ADC_H_

// Port Pins
// ADC
// PE3 => ADC0 (Sample)
// PE2 => ADC1 (Reference)

#define VDD	3.3
#define ADC_PRECISION	4096

extern void ADC_Init(void);
extern float ADC_VoltageDifference(float *voltage_sample, float *voltage_ref);

#endif /* ADC_H_ */

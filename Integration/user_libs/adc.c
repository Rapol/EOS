/*
 * adc.c
 *
 *  Created on: Nov 5, 2014
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
#include "driverlib/adc.h"
#include "adc.h"

// ADC Pins
// PE3 => ADC0 (Sample)
// PE2 => ADC1 (Reference)

uint32_t result_sample[8], result_ref[8];

void ADC_Init(void) {
//	SysCtlClockSet(
//	SYSCTL_SYSDIV_5 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ);

	SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);	// PE3
//	ADCHardwareOversampleConfigure(ADC0_BASE, 64);

	ADCSequenceConfigure(ADC0_BASE, 0, ADC_TRIGGER_PROCESSOR, 0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 0, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 1, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 2, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 3, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 4, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 5, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 6, ADC_CTL_CH0);
	ADCSequenceStepConfigure(ADC0_BASE, 0, 7,
	ADC_CTL_CH0 | ADC_CTL_IE | ADC_CTL_END);

	SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC1);	// PE2
//	ADCHardwareOversampleConfigure(ADC1_BASE, 64);

	ADCSequenceConfigure(ADC1_BASE, 0, ADC_TRIGGER_PROCESSOR, 0);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 0, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 1, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 2, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 3, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 4, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 5, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 6, ADC_CTL_CH1);
	ADCSequenceStepConfigure(ADC1_BASE, 0, 7,
	ADC_CTL_CH1 | ADC_CTL_IE | ADC_CTL_END);

	ADCSequenceEnable(ADC0_BASE, 0);
	ADCSequenceEnable(ADC1_BASE, 0);
}

//------------ADC_InSeq3------------
// Busy-wait analog to digital conversion
// Input: none
// Output: 8-bit result of ADC conversion
float ADC_VoltageDifference(float *voltage_sample, float *voltage_ref) {

//	ADCIntClear(ADC0_BASE, 0);
	ADCProcessorTrigger(ADC0_BASE, 0);

	while (!ADCIntStatus(ADC0_BASE, 0, false))
		;

	ADCSequenceDataGet(ADC0_BASE, 0, result_sample);

//	ADCIntClear(ADC1_BASE, 0);
	ADCProcessorTrigger(ADC1_BASE, 0);

	while (!ADCIntStatus(ADC1_BASE, 0, false))
		;

	ADCSequenceDataGet(ADC1_BASE, 0, result_ref);

	// Get the voltage averages
	int j;
	volatile uint32_t result_sample_avg = 0, result_ref_avg = 0;
	for (j = 0; j < 8; j++) {
		result_sample_avg += result_sample[j];
		result_ref_avg += result_ref[j];
	}
	result_sample_avg = result_sample_avg / 8.0;
	result_ref_avg = result_ref_avg / 8.0;

	// Calculate the voltage of the sample
	*voltage_sample = result_sample_avg * VDD / ADC_PRECISION;

	// Calculate the reference voltage
	*voltage_ref = result_ref_avg * VDD / ADC_PRECISION;

	float voltage_result = *voltage_ref - *voltage_sample;
	if (voltage_result < 0)
		voltage_result = (-1) * voltage_result;

	return voltage_result;
}

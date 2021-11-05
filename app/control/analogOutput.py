from os import error
from threading import Thread
from setup_MCP4725 import Septup_MCP4725
from queue import Queue
from random import randint
from time import sleep
class AnalogOutput(Thread):
    def __init__(self, minInput,maxIput,minOutput,maxOutput,que_mass_flow,dac_device) -> None:
        super().__init__()
        self.runing=True
        self.minInput=minInput
        self.maxInput=maxIput
        self.minOutput=minOutput
        self.maxOutput=maxOutput
        self.que_mass_flow=que_mass_flow
        self.buffer_max_output=0
        self.buffer_max_output=0
        self.dac_device=dac_device
        self.value_mass_flow_is_ok=False
        self.voltage_now=0
    def convert_value(self,value):
        output=self.minOutput +(self.maxOutput-self.minOutput)/(self.maxInput-self.minInput)*(value-self.minInput)
        output=self.check_extreme_values(output)
        return output
    def check_extreme_values(self,value):
        saturation_value=value
        if value>self.maxOutput:
            self.buffer_max_output=value
            saturation_value=self.maxOutput
        if value<self.minOutput:
            self.buffer_min_output=value
            saturation_value=self.minOutput
        return saturation_value
    def run(self):
        while self.runing:
            if not self.que_mass_flow.empty():
                info_mass_flow=self.que_mass_flow.get()
                if info_mass_flow!=None:
                    mass_flow=float(info_mass_flow.get('mass_flow',0))
                    mass_flow_voltage=self.convert_value(mass_flow)
                    self.dac_device.output_voltage(mass_flow_voltage)
                    self.voltage_now=mass_flow_voltage
                    self.value_mass_flow_is_ok=True
                else:
                    self.value_mass_flow_is_ok=False
                    self.dac_device.output_voltage(0)
        self.dac_device.close_device()
if __name__=='__main__':
    try:# if an error raise this is going to let analogOutput closes the adc device
        ref_voltage_mv=3300
        dac=Septup_MCP4725('60',ref_voltage_mv)
        que_mass_flow=Queue()
        min_mass_flow=9
        min_output_voltage=0
        max_mass_flow=50
        max_output_voltage=3300
        analogOutput=AnalogOutput(min_mass_flow,max_mass_flow,min_output_voltage,max_output_voltage,que_mass_flow,dac)
        analogOutput.start()
        for i in range(10):
            mass_flow={'mass_flow':randint(min_mass_flow,max_mass_flow)}
            que_mass_flow.put(mass_flow)
            sleep(0.1)
            print(analogOutput.voltage_now)
            sleep(10)
        analogOutput.runing=False
    except error:
        print(error)
        analogOutput.runing=False


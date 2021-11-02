import sys
sys.path.append('../')
import time
MCP4725A0_IIC_Address0				= 0x60
MCP4725A0_IIC_Address1				= 0x61
from DFRobot_MCP4725 import MCP4725
mcp4725 = MCP4725()
REF_VOLTAGE   = 3300
OUTPUT_VOLTAGE = 2000
#Set the MCP225's i2c address
mcp4725.setAddr_MCP4725(MCP4725A0_IIC_Address1)
#Setting the base voltage of DAC must equal the power supply voltage, and the unit is millivolt
mcp4725.set_refVoltage(REF_VOLTAGE)
while True :
  #Output voltage value OUTPUT_VOLTAGE mV
	mcp4725.outputVoltage(OUTPUT_VOLTAGE)
	time.sleep(0.1)
	print ("DFRobot_MCP4725 output: %d mV"%OUTPUT_VOLTAGE)
	print (" ********************************************* ")
	time.sleep(0.8)

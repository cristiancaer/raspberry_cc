import DFRobot_MCP4725
import os
import shlex
import subprocess
import smbus
from DFRobot_MCP4725.DFRobot_MCP4725 import *
class Septup_MCP4725:
    # voltage must be in millivolts
    COMMAND_I2C_DETECT=shlex.split("i2cdetect -y 1")# shlex.split is needed to accommodate comand to subprocess function
    Message_INTERFACE_DISABLE="Interface disable. Check sudo raspi-config/ interface options/I2C"
    MESSAGE_INTERFACE_ENABLE="Interface up"
    Message_DAC_NOT_FIND=" module in addresses no detected, addr: "
    MESSAGE_DAC_DETECTED="You can start to work. Device detected in "
    MESSAGE_LIST_DEVISE_DETECTED="Device detected: "
    MCP4725A0_IIC_Address0=61
    MCP4725A0_IIC_Address1=60
    addr=""
    is_working=False
    ref_voltage=1000
    
    def __init__(self,addr) -> None:
        self.set_addr_(addr)

        if  self.i2c_interface_is_enable:
            print("Interface up")
            detected,list_device_chanel6=self.device_detected(chanel=6)
            if detected:
                print(self.MESSAGE_DAC_DETECTED, self.addr)
                self.is_working=True
            else:
                print(self.Message_DAC_NOT_FIND)
                print(self.MESSAGE_LIST_DEVISE_DETECTED,list_device_chanel6)
        else:
            print(self.Message_INTERFACE_DISABLE)
        
    def clear_cli(self):
        os.system('clear')
    
    def i2c_interface_is_enable(self):
        status,_=self.run_command(self.COMMAND_I2C_DETECT)
        check=False
        if status==0:# command run successfully, output stdout type=0, interface enable
            check=True
        return check

    def run_command(self,command):
        output=subprocess.run(command,check=True,encoding='utf-8',capture_output=True)
        status=output.returncode
        stdout=output.stdout
        return status,stdout
    
    def device_detected(self,chanel):
        _,output=self.run_command(self.COMMAND_I2C_DETECT)
        row_addresses_chanel=output.split("\n")[chanel+1]# 0 row is head,addresses start in row 1, so row 7 belongs to divices whit 6x addresses
        list_addresses_chanel=row_addresses_chanel.split(' ')[1:]# 0 column is head,addresses start in col 1
        is_device=self.addr in list_addresses_chanel
        return is_device,list_addresses_chanel
    
    def set_addr_(self,addr):
        self.addr=addr
    
    def set_ref_voltage(self,vol):
        self.ref_voltage=vol
    
    def output_voltage(self,vol):
        vol=self.check_saturation(vol)
        self.bus.write_word_data(self.addr,MCP4725_Write_CMD | (MCP4725_NORMAL_MODE<<1),int((vol/float(self.ref_voltage))*255))  
    
    def output_voltage_EEPROM(self,vol):
        self.bus.write_word_data(self.addr,MCP4725_WriteEEPROM_CMD | (MCP4725_NORMAL_MODE<<1),int((vol/float(self.ref_voltage))*255))
    def check_saturation(self,vol):
        output=vol
        if vol>self.ref_voltage:
            output=self.ref_voltage
        if vol<0:
            output=0
        return output
if __name__=='__main__':
    dac=Septup_MCP4725('60')
    # if dac.is_working:
    #     vol_ref=int(input("reference voltage [mv]?:"))
    #     dac.set_ref_voltage(vol_ref)
    #     while True:
    #         vol=input("voltage output [mv]? :")
    #         if vol.isnumeric:
    #             vol=int(vol)
    #             dac.clear_cli
    #         else:
    #             break
            
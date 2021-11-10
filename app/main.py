from control.analogOutput import *
from control.setup_MCP4725 import *
from control.communication import *
from threading import Thread
from queue import Queue
from time import sleep
from datetime import datetime
import traceback
class App(Thread):
    def __init__(self):
        super().__init__()
        self.app_running=True
        # Dac Config
        self.ref_voltage_mv=3300
        self.addr='60'
        self.dac=Septup_MCP4725(self.addr,self.ref_voltage_mv)
        #analogOput config
        self.que_mass_flow=Queue()
        self.min_mass_flow=9
        self.max_mass_flow=60
        self.min_output_voltage_mv=0
        self.max_output_voltage_mv=self.ref_voltage_mv
        self.analog_output=AnalogOutput(self.min_mass_flow,self.max_mass_flow,self.min_output_voltage_mv,self.max_output_voltage_mv,self.que_mass_flow,self.dac)
        self.analog_output.start()
        # comunication config
        self.url='http://112.168.1.1:5000'
        self.communication=Communication(self.url,self.que_mass_flow)
        self.communication.set_raspberry_status(self.update_raspberry_status)
        self.communication.start()
        # list menu functions
        self.MENU_OPTIONS=['Status dac is working: ',
                  'Status i2c interface is up: ',
                  'Status len que_mass_flow: ',
                  'Status  server is working: ',
                  'Ref dac voltage :',
                  'Voltage dac now: ',
                  'I2c available direcctions: ',
                  'Communication status message: ',
                  'exit: '
                 ]
        self.menu_functions=[ lambda:self.dac.is_working,
                              self.dac.i2c_interface_is_enable,
                              self.que_mass_flow.qsize,
                              lambda: self.communication.server_is_working,
                              lambda:self.dac.ref_voltage,
                              lambda:self.analog_output.voltage_now,
                              self.get_list_device_i2c_detected,
                              self.communication.get_total_status_message_com,
                              self.close
                            ]
    
    def run(self):
        print("hi")
        value_result=""
        try:
            while self.app_running:
                system('clear')
                print(value_result)
                print("output_voltage: ",app.analog_output.voltage_now)
                for i,option in enumerate(self.MENU_OPTIONS):
                    print('{}) '.format(i+1),option)
                menu_option=input("press en option: ")
                if menu_option and (menu_option.isnumeric):
                    menu_option=int(menu_option)-1
                    if  menu_option in range(len(self.MENU_OPTIONS)):
                        value_result=self.MENU_OPTIONS[menu_option]
                        value_result+=str(self.menu_functions[menu_option]())
                    else:
                        value_result="Option  not recognized"

                else:
                    value_result="Input must be a number"
        except Exception :
            traceback.print_exc()
            print('main interrupted')
            self.close()
    def close(self):
        self.app_running=False
        self.communication.running=False
        self.analog_output.runing=False
    def get_list_device_i2c_detected(self):
        _,list_device=self.dac.device_detected(chanel=6)
        return list_device
    def update_raspberry_status(self):
        #all in dictionary must be a strings
        dict_status={str(self.MENU_OPTIONS[i]):str(self.menu_functions[i]()) for i in range(len(self.MENU_OPTIONS)-1)}# beware! last option function is gonna to close de app 
        dict_status['datetime']=datetime.now().strftime("%y-%m-%d %H:%M:%S")
        datetime.now().sr
        return dict_status
if __name__=='__main__':
    app=App()
    app.start()
    try: 
        while True:
            # print(app.get_app_message())
            # print("output_voltage: ",app.analog_output.voltage_now)
            if not app.app_running:
                break
            sleep(5)
    except Exception:
        traceback.print_exc()
        print('forced stop')
        app.close()

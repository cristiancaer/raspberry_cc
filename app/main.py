import queue
from control.analogOutput import *
from control.setup_MCP4725 import *
from control.communication import *
from threading import Thread
from queue import Queue
from time import sleep
class App(Thread):
    def __init__(self):
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
        self.analogOutput=AnalogOutput(self.min_mass_flow,self.max_mass_flow,self.min_output_voltage_mv,self.max_output_voltage_mv,self.que_mass_flow,self.dac)
        self.analogOutput.start()
        # comunication config
        self.url='http://112.168.1.1:5000'
        self.comunication=Communication(self.url,self.que_mass_flow)
        self.comunication.start()
        # list menu functions
        self.MENU_OPTIONS=['Status dac is working: ',
                  'Status i2c interface is up: ',
                  'Status len que_mass_flow: ',
                  'Status  server is working: ',
                  'Ref dac voltage :',
                  'Voltage dac now: ',
                  'Communication status message: '
                  'exit: '
                 ]
        self.menu_functions=[ self.dac.is_working(),
                              self.dac.i2c_interface_is_enable(),
                              self.que_mass_flow.qsize(),
                              lambda: self.comunication.server_is_working,
                              lambda:self.dac.ref_voltage,
                              lambda:self.analogOutput.voltage_now,
                              self.communication.get_message_status(),
                              sys.exit(0)
                            ]

    def run(self):
        value_result=""
        try:
            while True:
                system('clear')
                print(value_result)
                for i,option in enumerate(self.MENU_OPTIONS):
                    print(f'{i+1}) ',option)
                menu_option=input("press en option: ")
                if menu_option.isnumeric:
                    menu_option=int(menu_option)-1
                    if  menu_option in range(len(self.MENU_OPTIONS)):
                        value_result=f'{i+1}) '+self.MENU_OPTIONS[i]
                        value_result+=self.menu_functions[menu_option]
                    else:
                        value_result="Option  not recognized"

                else:
                    value_result="Input must be a number"
        except:
            print('main interrupted')
            self.analogOutput.runing=False
    def get_app_message(self):
        return self.comunication.status_message
if __name__=='__main__':
    app=App()
    app.start()
    while True():
        print(app.get_app_message())
        sleep(5)
    
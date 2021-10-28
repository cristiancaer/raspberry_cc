import requests
from threading import Thread
from queue import Queue
from time import sleep
from bs4 import BeautifulSoup
class Communication(Thread):
    def __init__(self,url,que_mass_flow) -> None:
        super().__init__(daemon=True)
        self.url=url
        self.que=que_mass_flow
        self.running=True
        self.separator='---'
        self.watchdog=5# number of times witout request before raise exception
        self.time_betwin_request=2# in seconds
        self.server_is_working=False
        self.ERROR_WEB_SERVER_NOT_WORKING="Web server is not working"
        self.ERROR_NO_DATA_AVAILABLE="Server working. But mass_flow.py isn't loading data"
    def get_last_data(self):
        try:
            res= requests.get(self.url)
            self.server_is_working=True
        except :
            print(self.ERROR_WEB_SERVER_NOT_WORKING)
            self.server_is_working=False
        info={}
        if self.server_is_working:
            soup=BeautifulSoup(res.text,'html.parser')
            data=soup.find_all(class_='data')
            for tag in data:
                tag=tag.text.strip()
                key,value=tag.split(self.separator)
                info.setdefault(key,value)
        return info
    def run(self) -> None:
        while self.running:
            info=self.get_last_data()
            if self.server_is_working:
                if info:
                    self.que.put(info)
                    self.watchdog=5
                else:
                    if  self.watchdog:
                        self.watchdog-=1
                    else:
                        print(self.ERROR_NO_DATA_AVAILABLE)
                        self.que.put(None)
                
            sleep(2)
class AnalogOput(Thread):
    def __init__(self, minInput,maxIput,minOutput,maxOutput,que_mass_flow) -> None:
        super().__init__(daemon=True)
        self.runing=True
        self.minInput=minInput
        self.maxInput=maxIput
        self.minOutput=minOutput
        self.maxOutput=maxOutput
        self.que_mass_flow=que_mass_flow
    def convert_value(self,value):
        output=self.minOutput +(self.maxOutput-self.minOutput)/(self.maxInput-self.minInput)*(value-self.minInput)
        return output
    def run(self):
        while self.runing:
            if not self.que_mass_flow.empty():
                info_mass_flow=self.que_mass_flow.get()
                if info_mass_flow!=None:
                    mass_flow=float(info_mass_flow.get('mass_flow',0))
                    mass_flow_voltage=self.convert_value(mass_flow)
                    print('mass',mass_flow)
                    print('voltage',mass_flow_voltage)




if __name__=='__main__':
    que_mass_flow=Queue()
    url='http://127.0.0.1:5000/connection/data_available/'
    comm=Communication(url,que_mass_flow)
    comm.start()
    analogOutput=AnalogOput(0,1,0,5,que_mass_flow)
    analogOutput.start()
    
    while True:
        c=input("press c to exit: ")
        if c=='c':
            comm.running=False
            analogOutput.runing=False
            break


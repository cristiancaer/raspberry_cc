import requests
from threading import Thread
from queue import Queue
from time import sleep, time
from bs4 import BeautifulSoup
from os import system
class Communication(Thread):
    def __init__(self,url,que_mass_flow) -> None:
        super().__init__(daemon=True)
        self.url_server=url
        self.url_get_data='/connection/data_flow_available/'
        self.que=que_mass_flow
        self.running=True
        self.separator='---'
        self.watchdog=5# number of times witout request before raise exception
        self.time_betwin_request=2# in seconds
        self.server_is_working=False
        self.ERROR_WEB_SERVER_NOT_WORKING="Web server is not working. \n 1) Check if there is IP/ethernet connection.\n 2) Check if server is up.\n 3) Check if url is correct"
        self.ERROR_WRONG_URL=" page not find. Check url for data_available  in Connection class"
        self.ERROR_NO_DATA_AVAILABLE="Server working. But mass_flow.py isn't loading data"
        self.ALL_IS_OK='All in communication is ok'
        self.TIMEOUT=3
        self.requests=requests.session()
        self.status_message=''
    # check sever is working
        self.check_server()
    def check_server(self):
        self.get_request_from_page('/index/')
    def get_request_from_page(self,url_page):
        res=404
        try:
            url=self.url_server+url_page
            res= self.requests.get(url,timeout=self.TIMEOUT)
            if res.status_code==200:
                self.server_is_working=True
                self.status_message=self.ALL_IS_OK
            elif res.status_code==404:
                self.status_message=self.ERROR_WRONG_URL
        
        except:
            self.status_message=self.ERROR_WEB_SERVER_NOT_WORKING
            self.server_is_working=False
        return res
    def get_last_data(self):
        res=self.get_request_from_page(self.url_get_data)
        info={}
        if self.server_is_working:
                soup=BeautifulSoup(res.text,'html.parser')
                data=soup.find_all(class_='data')
                for tag in data:
                    tag=tag.text.strip()
                    key,value=tag.split(self.separator)
                    info.setdefault(key,value)
                
        return info
    def download_data(self):
        info=self.get_last_data()
        if info:
            self.que.put(info)
            self.watchdog=5
        else:
            if  self.watchdog:
                self.watchdog-=1
            else:           
                self.que.put(None)
                self.status_message=self.ERROR_NO_DATA_AVAILABLE
    def run(self) -> None:
        while self.running:

            if self.server_is_working:
                self.download_data()
            else: 
                self.check_server()
            sleep(2)
    def get_status_message(self):
        return self.status_message
def print_que(que,message):
    buffer_message=""
    while True:
        if buffer_message!=message():
            system('clear')
            buffer_message=message()
            print(buffer_message)
            print('press c to exit')
        if not que.empty():
            print(que.get())

if __name__=='__main__':
    system('clear')
    que_mass_flow=Queue()
    url='http://112.168.1.1:5000'
    comm=Communication(url,que_mass_flow)
    comm.start()
    work=Thread(target=print_que,args=(que_mass_flow,comm.get_status_message),daemon=True)
    work.start()
    while True:
        c=input("press c to exit: \n")
        if c=='c':
            comm.running=False
            break


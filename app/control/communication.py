import requests
from threading import Thread
from queue import Queue
from time import sleep, time
from bs4 import BeautifulSoup
from os import system

class Communication(Thread):
    def __init__(self,url,que_mass_flow,function_update_raspberry_status=0) -> None:
        super().__init__(daemon=True)
        self.function_update_raspberry_status=function_update_raspberry_status
        self.url_server=url
        self.url_get_data='/connection/data_flow_available/'
        self.url_put_raspberry_status='/connection/put_raspberry_status/'
        self.que=que_mass_flow
        self.running=True
        self.separator='---'
        self.watchdog=5# number of times witout request before raise exception
        self.time_betwin_request=2# in seconds
        self.server_is_working=False
        self.ERROR_WEB_SERVER_NOT_WORKING="Web server is not working. \n 1) Check if there is IP/ethernet connection.\n 2) Check if server is up.\n 3) Check if url is correct"
        self.ERROR_WRONG_URL="Page not find. Check url for data_available  in Communication class"
        self.ERROR_NO_DATA_AVAILABLE="Server working. But mass_flow.py isn't loading data"
        self.ALL_IS_OK='All in communication is ok'
        self.CONNECTING='Waiting'
        self.TIMEOUT=3
        self.requests=requests.session()
        self.status_message_comm={'server_working':'No message',
                                  'get_last':'No message',
                                  'sent_raspberry_status':'No mesage'
        }
        self.raspberry_status={}
    # check sever is working
        self.check_server()
    def reset_message(self):
        for key in self.status_message_comm.keys():
            if key!='server_working':
                self.status_message_comm[key]='No message'
    def check_server(self):
        res,_=self.get_request_from_page('/index/')
        self.reset_message()
        
    def make_request(self,url_page,type_request='GET',dictionary={}):
        res=404
        status_message='No message'
        try:
            url=self.url_server+url_page
            if type_request=='GET':
                res= self.requests.get(url,timeout=self.TIMEOUT)
            else:
                res=self.requests.post(url,timeout=self.TIMEOUT,json=dictionary) 
            if res.status_code==200:
                status_message=self.ALL_IS_OK
            elif res.status_code==404:
                status_message=self.ERROR_WRONG_URL
            self.server_is_working=True
            self.status_message_comm['server_working']='True'

        except:
            self.status_message_comm['server_working']=self.ERROR_WEB_SERVER_NOT_WORKING
            self.server_is_working=False
        return res,status_message
    def get_request_from_page(self,url_page):
        res,status_message=self.make_request(self.url_get_data,type_request='GET')
        return res,status_message
    def json_post_request_to_page(self,url_page,dictionary):
        res,status_message=self.make_request(url_page,type_request='POST',dictionary=dictionary)
        return res,status_message
    def get_last_data(self):
        res,status_message=self.get_request_from_page(self.url_get_data)
        self.status_message_comm['get_last']=status_message
        info=None
        if self.server_is_working:
            if res.status_code!=404:
                    soup=BeautifulSoup(res.text,'html.parser')
                    data=soup.find_all(class_='data')
                    if not data:
                        if  self.watchdog:
                            self.watchdog-=1
                        else:           
                            self.status_message_comm['get_last']=self.ERROR_NO_DATA_AVAILABLE
                    else:
                        self.watchdog=5
                        for tag in data:
                            tag=tag.text.strip()
                            key,value=tag.split(self.separator)
                            info.setdefault(key,value)
        return info
    def download_data(self):
        info=self.get_last_data()
        if info:
                self.que.put(info)


                
    def run(self) -> None:
        while self.running:
            self.download_data()
            self.upload_data()
            if not self.server_is_working: 
                self.check_server()
            sleep(2)

    def get_total_status_message_com(self):
        message=''
        for key,value in self.status_message_comm.items():
            message+=key+': \n'+value+'\n'
        return message
    
    def upload_data(self):
        if self.server_is_working:
            self.send_raspberry_status()
        # self.send_humidity_value()
    def send_raspberry_status(self):
        self.raspberry_status=self.function_update_raspberry_status()
        res,status_message=self.json_post_request_to_page(self.url_put_raspberry_status,self.raspberry_status)
        self.status_message_comm['sent_raspberry_status']=status_message
        if res==404:
            print(self.get_status_message)
    def set_raspberry_status(self,funcition_update):
        self.function_update_raspberry_status=funcition_update
    def get_raspberry_status(self):
        return self.raspberry_status
def print_que(que,message,status):
    buffer_message=""
    while True:
        if buffer_message!=message()+str(status()):
            system('clear')
            buffer_message=message()+str(status())
            print(message())
            print(status())
            print('press c to exit')
        if not que.empty():
            print(que.get())
def update_status():
    dic_status={'{}'.format(i):i for i in range(11)}
    return dic_status
if __name__=='__main__':
    system('clear')
    que_mass_flow=Queue()
    url='http://112.168.1.1:5000'
    comm=Communication(url,que_mass_flow)
    comm.start()
    work=Thread(target=print_que,args=(que_mass_flow,comm.get_total_status_message_com,comm.get_raspberry_status),daemon=True)
    work.start()
    status={'{}'.format(i):i for i in range(10)}
    print(status)
    comm.set_raspberry_status(update_status) # if a variable is just pass, Python make a copy from the variable, so it must be a funcition
    while True:
        c=input("press c to exit: \n")
        if c=='c':
            comm.running=False
            break


from threading import Thread 
from queue import Queue
import time
import socket
import sys
import atexit
import pandas as pd
from openpyxl import Workbook

timeout=1
ts_r=Queue()
ts_s=Queue()
workbook = Workbook()

def Client_app(Ts_r,Ts_s):
    time.sleep(1)
    #client
    host = 'gpsdev.tracksolid.com'
    port = 21100  # web
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('# Getting remote IP address')
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
    # Connect to remote server
    print('# Connecting to server, ' + host + ' (' + remote_ip + ')')
    s.connect((remote_ip , port))
    while True:
        data=Ts_s.get(block=True, timeout=None)
        try:
            s.sendall(data)
        except socket.error:
            print ('Send failed')
            # sys.exit()
        reply = s.recv(4096)
        Ts_r.put(reply)
        
def Main_app(Ts_r,Ts_s):
    #server 
    HOST = "110.120.103.100" #str(sys.argv[1]) #'192.168.1.2'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    print('waiting for a connection')
    connection, client_address = sock.accept()
    print('connection from'+str(client_address))
    while True:
        data = connection.recv(4096)
        print (f'{time.ctime()}:received "{data}"')
        Ts_s.put(data)
        try:
            reply=Ts_r.get(timeout=timeout)
            # print ('sending data back to the client')
            connection.sendall(reply)
            print (f'{time.ctime()}:reply "{reply}"' )
        except:
            reply=None
            pass
        sheet=workbook.active
        sheet.insert_rows(idx=1)
        sheet["A1"]=str(time.ctime())
        sheet["B1"]=str(data)
        sheet["C1"]=str(reply)
        workbook.save("log.xlsx")


t1 = Thread(target = Main_app, args =(ts_r,ts_s) )
t2 = Thread(target = Client_app, args =(ts_r,ts_s) )


t1.start()
t2.start()
#!/usr/bin/env python3

import socket
import sys
import time
import pandas as pd

exported_list=list()

#server 
HOST = "110.120.103.100" #str(sys.argv[1]) #'192.168.1.2'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()

#client
host = 'gpsdev.tracksolid.com'
port = 21100  # web
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('# Getting remote IP address')
try:
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    print('Hostname could not be resolved. Exiting')
    sys.exit()
# Connect to remote server
print('# Connecting to server, ' + host + ' (' + remote_ip + ')')
while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    s.connect((remote_ip , port))
    try:
        print('connection from'+str(client_address))
       # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4096)
            print ('received "%s"' % data)

            #client
            print ('send data to track solid')
            try:
                s.sendall(data)
            except socket.error:
                print ('Send failed')
                sys.exit()
            reply = s.recv(4096)
            print ('reply "%s"' % reply)
            
            exported_list.append([str(time.ctime()),data,reply])
            #send to x3
            if data:
                print ('sending data back to the client')
                connection.sendall(reply)
            else:
                print ('no more data from', client_address)
                break
    except:
        print("ridi haji")
connection.close()
# Clean up the connection
df = pd.DataFrame(exported_list)
writer = pd.ExcelWriter(str(time.time())+'.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='welcome', index=False)
writer.save()

import numpy as np
import matplotlib.pyplot as plt
import socket

# 本機位置
ip = socket.gethostbyname(socket.gethostname())
port = 8080

server_address_family = (ip,port)       #伺服器地址族

client = socket.socket()
client.connect(server_address_family)
msg = client.recv(5120)

tmp = 10 #要傳的資料

if msg:
    print("\n----------Send----------")
    client.send(tmp.encode('utf-8'))
    print('client send the amout of object : ' + tmp)
    msg = client.recv(5120)
    print('recv: ' + msg.decode('utf-8'))

    print("----------Done----------\n")
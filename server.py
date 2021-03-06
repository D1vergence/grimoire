﻿import socket,time
import threading
import model,unit
import pickle
import ctrl

pickle_model=b''

def my_send(sock,data):
    sock.send( str(len(data)).ljust(16).encode('utf8') )
    sock.send( data )

def server(address):
    address = (address, 8003)
    player_pool=dict()
    def tcplink(sock,addr):
        print('从',addr,'连进来了')
        h=hash(addr[0])
        if h in player_pool:
            you=player_pool[h]
        else:
            you=ctrl.player()
            player_pool[h]=you

        f_s=sock.recv(4)
        if f_s[:2]==b'ct':
            you.set_hero(int(f_s[2:4]))

        while True:
            s=sock.recv(13)
            if s==b'':
                time.sleep(0.1)
            if s==b'cnm----------':
                my_send(sock,pickle_model)
                my_send(sock,pickle.dumps(you.info))
            if s[:3]==b'mov':
                you.ctrler.mov(int(s[3:8]),int(s[8:13]))
            if s[:2]==b'mg':
                # print(s[3:8])
                you.ctrler.magic(chr(s[2]),int(s[3:8]),int(s[8:13]))
            if s[:3]==b'hod':
                you.ctrler.hold()
                
        print('与',addr,'的连接断开了')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(address)
    s.listen(True)
    
    while True:
        time.sleep(0.01)
        sock, addr = s.accept()
        t = threading.Thread(target=tcplink, args=(sock,addr))
        t.start()

t = threading.Thread(target=lambda:server('0.0.0.0'))
t.setDaemon(True)
t.start()



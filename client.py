import pygame
from pygame.locals import *
from sys import exit
import random
import pickle
rd = random.randint
from screen import screen
import socket
import os
from tool import *
import time
import threading
import config
import map

os.system('title 客户端')

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode(config.scr_size, 0, 32)
# screen = pygame.display.set_mode(config.scr_size,(pygame.FULLSCREEN),32)
import model

background = pygame.image.load(config.bg_img).convert()

def go(x):
    t = eval('model.%s(t=%s)' % (x.split('(')[0], x.split(',')[2]  ))
    t.x = int( x.split(',')[0].split('(')[1]  )
    t.y = int( x.split(',')[1]  )
    model_pool.append(t)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def my_rec(sock):    
    length = recvall(sock,16)
    data = recvall(sock, int(length))
    return data

def write_word(word,x,y,color=(255,255,255)):
    if type(word)==int or type(word)==float:
        word='%.2f'%word
    if word=='0.00':
        color=(222,222,0)
    font_surface = font.render(word, True, (0,0,0))
    screen.blit(font_surface, (x  , y ))
    font_surface = font.render(word, True, color)
    screen.blit(font_surface, (x+1,y+1))
    
    
font = pygame.font.SysFont('SimHei', 24)


sock2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock2.connect(config.server_addr)
sock2.send(b'ct0'+str(config.hero).encode())

def suc(p):
    return str(p[0]).zfill(5)+str(p[1]).zfill(5)

   
model_pool=[]
info=['',[],[0,0],[0,0],0]

#和服务器数据交换这地方我真不知道怎么写2333333
def one_exchange(sock):
    while True:
        sock.send(b'cnm----------')
        global model_pool,info
        data = my_rec(sock)
        model_pool=pickle.loads(data)
        model_pool.sort(key=lambda i :i.z_index)
        data = my_rec(sock)
        info=pickle.loads(data)
    
def exchange():
    for i in range(5):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(config.server_addr)
        sock.send(b'mdzz')
        t = threading.Thread(target=lambda:one_exchange(sock),)
        t.setDaemon(True)
        t.start()
    
t = threading.Thread(target=exchange)
t.setDaemon(True)
t.start()
    
def correct_lense(t):
    t*=750
    r,c=config.scr_size
    x,y=(0,0)
    if pygame.mouse.get_pos()[0]<20: x=1
    if pygame.mouse.get_pos()[0]>r-21: x=-1
    if pygame.mouse.get_pos()[1]<20: y=1
    if pygame.mouse.get_pos()[1]>c-21: y=-1
    global x_dif,y_dif
    x_dif+=x*t
    y_dif+=y*t
    x_dif=limit(x_dif,config.scr_size[0]-map.size[0],0)
    y_dif=limit(y_dif,config.scr_size[1]-map.size[1],0)
    
def correct_mouse():
    l=list(pygame.mouse.get_pos())
    l[0]-=int(x_dif)
    l[1]-=int(y_dif)
    return l
    
    
x_dif,y_dif=(0,-3000)
suf=pygame.Surface(map.size)
s_map=pygame.Surface((200,200))
while True:
    time_pass=clock.tick() / 1000
    time_log(time_pass)
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == MOUSEBUTTONDOWN:
            data='mov'+suc(correct_mouse())
            # print(data.encode())
            sock2.send(data.encode())
        if event.type == KEYDOWN:
            data=''.ljust(13)
            p = correct_mouse()
            if event.key!=ord('s') and event.key<128:
                data= 'mg'+chr(event.key) +suc(p)
                # print(data)
            if event.key==ord('s'):
                data='hod'+suc(p)
            sock2.send(data.encode())

    correct_lense(time_pass)
    suf.blit(background, (0,0))
    # suf.fill([0,0,0])
    for i in model_pool:
        i.draww(suf)

    pygame.transform.scale(suf,(200,200), s_map)
    # print()
    screen.blit(suf, (x_dif,y_dif))
    screen.blit(s_map, (0,0))

    # print(info)
    mid=config.scr_size[0]/2
    write_word('exp:%d'%info[4],mid,config.scr_size[1]-85)
    write_word('%d'%info[2][0],mid,   config.scr_size[1]-60,color=(255,150,150))
    write_word('/',            mid+40,config.scr_size[1]-60)
    write_word('%d'%info[2][1],mid+52,config.scr_size[1]-60,color=(255,150,150))

    write_word('%d'%info[3][0],mid,   config.scr_size[1]-40,color=(170,170,255))
    write_word('/',            mid+40,config.scr_size[1]-40)
    write_word('%d'%info[3][1],mid+52,config.scr_size[1]-40,color=(170,170,255))
    
    x=config.scr_size[0]-300
    y=config.scr_size[1]-70*len(info[1])-40
    for i in info[1]:
        y+=40
        write_word(i[0],x,y)
        y+=30
        write_word(i[1],x,y,color=(162,162,255))
        
        

    pygame.display.update()
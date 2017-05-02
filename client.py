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

os.system('title 客户端')
scr_size=(1366,768)
bg_img='bg.png'
server_addr=('127.0.0.1',8003)
hero=2

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode(scr_size, 0, 32)
# screen = pygame.display.set_mode((1366, 768),(pygame.FULLSCREEN),32)
import model

background = pygame.image.load(bg_img).convert()

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
sock2.connect(server_addr)
sock2.send(b'ct0'+str(hero).encode())

def suc(p):
    return str(p[0]).zfill(5)+str(p[1]).zfill(5)

   
model_pool=[]
info=['',[],[0,0],[0,0]]

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
        sock.connect(server_addr)
        sock.send(b'mdzz')
        t = threading.Thread(target=lambda:one_exchange(sock),)
        t.setDaemon(True)
        t.start()
    
t = threading.Thread(target=exchange)
t.setDaemon(True)
t.start()
    


while True:
    time_log(clock.tick() / 1000)
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == MOUSEBUTTONDOWN:
            data='mov'+suc(pygame.mouse.get_pos())
            sock2.send(data.encode())
        if event.type == KEYDOWN:
            data=''.ljust(13)
            p = pygame.mouse.get_pos()
            if event.key==ord('q'):
                data='000'+suc(p)
            if event.key==ord('w'):
                data='001'+suc(p)
            if event.key==ord('e'):
                data='002'+suc(p)
            if event.key==ord('r'):
                data='003'+suc(p)
            if event.key==ord('s'):
                data='hod'+suc(p)
            sock2.send(data.encode())

    screen.blit(background, (0,0))
    
    for i in model_pool:
        i.draww(screen)
    # print(info)
    write_word(info[0],600,680)
    write_word('%d'%info[2][0],600,720,color=(255,150,150))
    write_word('/',            640,720)
    write_word('%d'%info[2][1],652,720,color=(255,150,150))
    
    write_word('%d'%info[3][0],600,740,color=(170,170,255))
    write_word('/',            640,740)
    write_word('%d'%info[3][1],652,740,color=(170,170,255))
    
    x=1200
    y=440
    for i in info[1]:
        y+=40
        write_word(i[0],x,y)
        y+=30
        write_word(i[1],x,y,color=(162,162,255))

    pygame.display.update()
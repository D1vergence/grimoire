import pygame
import random
rd = random.randint
rdth = lambda: random.random()*2*3.1415926
rdp = lambda: (random.random()-0.5)*0.3+1
from math import sin,cos
import screen
import copy
import config
from tool import *


model_pool_bk=[]
model_pool=[]

img_pool=dict()

if not config.server_mode:
    pygame.font.init()

class model():
    def __init__(self,t=99999999):
        self.max_time=t
        self.life_time=t
        self.iki=True
        self.z_index=0      #层叠顺序
    def time_pass(self,time):
        self.life_time-=time
        if self.life_time<=0:
            self.die()
    def draw(self,screen):
        self.face=self.owner.face
        self.x=self.owner.v.x
        self.y=self.owner.v.y
        try:
            self.hp=self.owner.hp
            self.maxhp=self.owner.maxhp
            self.mana=self.owner.mana
            self.max_mana=self.owner.max_mana
        except:
            None
        global model_pool
        t=copy.copy(self)
        t.owner=None
        model_pool.append(t)
        if not config.server_mode:
            self.draww(screen)
    def die(self):
        self.iki=False

class 方块(model):
    def __init__(self,t=99999999,r=20):
        super().__init__(t)
        self.r=r
    def draww(self,screen):
        r=self.r
        t=self.max_time-self.life_time
        if t<0.3:
            r=int(t/0.4*r)
        pygame.draw.rect(screen, (255,255,255), (self.x-r,self.y-r,r*2,r*2))

class 直线(model):
    def __init__(self,t=99999999,l=20,color=(255,255,255),width=3):
        super().__init__(t)
        self.l=l
        self.color=color
        self.width=width
    def draww(self,screen):
        v=self.face*self.l
        pygame.draw.line(screen, self.color, (self.x,self.y),(self.x-v.x,self.y-v.y),self.width)
        
class 箭头(model):
    def __init__(self,t=99999999,l=20,color=(255,255,255),width=3):
        super().__init__(t)
        self.l=l
        self.color=color
        self.width=width
    def draww(self,screen):
        v=self.face*self.l
        pygame.draw.line(screen, self.color, (self.x,self.y),(self.x-v.x,self.y-v.y),self.width)
        v1=v.adjust_angle(3.14/4)*0.5
        pygame.draw.line(screen, self.color, (self.x,self.y),(self.x-v1.x,self.y-v1.y),self.width)
        v2=v.adjust_angle(-3.14/4)*0.5
        pygame.draw.line(screen, self.color, (self.x,self.y),(self.x-v2.x,self.y-v2.y),self.width)
        
class 圆形(model):
    def __init__(self,t=99999999,r=15):
        super().__init__(t)
        self.r=r
    def draww(self,screen):
        r=self.r
        t=self.max_time-self.life_time
        if t<0.4:
            r=int(t/0.4*r)
        pygame.draw.circle(screen,[0,0,0],[int(self.x),int(self.y)],r+1)
        pygame.draw.circle(screen,[255,255,255],[int(self.x),int(self.y)],abs(r))

class 圆形消失(model):
    def __init__(self,t=99999999):
        super().__init__(t)
    def draww(self,screen):
        r=int(15*(self.life_time/self.max_time))
        pygame.draw.circle(screen,[255,255,255],[int(self.x),int(self.y)],abs(r))
        
class 十字(model):
    def __init__(self,t=99999999,color=(111,111,255)):
        super().__init__(t)
        self.color=color
    def draww(self,screen):
        pygame.draw.rect(screen, (0,0,0), (self.x-8,self.y-16,16,32))
        pygame.draw.rect(screen, (0,0,0), (self.x-16,self.y-8,32,16))
        pygame.draw.rect(screen, self.color, (self.x-7,self.y-15,14,30))
        pygame.draw.rect(screen, self.color, (self.x-15,self.y-7,30,14))
        
class 头像(model):
    def __init__(self,t=99999999,name=None):
        super().__init__(t)
        self.name=name
        self.z_index=1
    def draww(self,screen):
        if self.name not in img_pool:
            img_pool[self.name]= pygame.image.load('img/%s.png'%self.name).convert_alpha()
        screen.blit(img_pool[self.name], (self.x-20, self.y-20))
        
class 激光(model):
    def __init__(self,t=99999999,color=(255,255,255),pos=(0,0),r=20):
        super().__init__(t)
        self.color=color
        self.pos=pos
        self.r=r
        self.z_index=-10
    def draww(self,screen):
        p1=vec(self.x,self.y)
        p2=p1-(p1-self.pos)*9999
        r= abs(int(sin(self.life_time/self.max_time*3.14)*self.r))
        pygame.draw.line(screen,self.color,(p1.x,p1.y),(p2.x,p2.y), r)
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),int(r/2))
        
class 闪电(model):
    def __init__(self,t=99999999,tar=(0,0)):
        super().__init__(t)
        self.tar=vec(tar[0],tar[1])
        self.z_index=-10
    def draww(self,screen):
        p1=vec(self.x,self.y)
        p2=self.tar
        pre=p1
        color=(255-rd(30,150),255-rd(30,150),255)
        for i in range(4):
            p=((p2-p1)*(i/5)+p1).ran_dif(20)
            pygame.draw.line(screen,color,(pre.x,pre.y),(p.x,p.y), 3)
            pre=p
        pygame.draw.line(screen,color,(pre.x,pre.y),(p2.x,p2.y), 3)


class 闪光(model):
    def __init__(self,t=99999999,r=40):
        super().__init__(t)
        self.z_index=22
        self.r=r
    def draww(self,screen):
        for i in range(0,8):
            t=(3.14/4)*i
            p=max(0,1-self.life_time/self.max_time)
            x1=int(self.r*p**0.7*sin(t))
            y1=int(self.r*p**0.7*cos(t))
            x2=int(self.r*p**1.5*sin(t))
            y2=int(self.r*p**1.5*cos(t))
            pygame.draw.line(screen,(255,255,255),(self.x+x1,self.y+y1),(self.x+x2,self.y+y2), 3)

class 倒计时(model):
    def __init__(self,t):
        super().__init__(t)
        self.z_index=999
    def draww(self,screen):
        start_angle = 0+3.14/2
        end_angle = 2*3.14*(self.life_time/self.max_time)+3.14/2
        width = 3
        position = self.x-14,self.y-14,28,28
        pygame.draw.arc(screen,(0,0,0), position, start_angle, end_angle, width+4)
        start_angle += 0.15
        end_angle -= 0.15
        position = self.x-12,self.y-12,24,24
        pygame.draw.arc(screen,(0,255,0), position, start_angle, end_angle, width)
        
class 晕眩(model):
    def __init__(self,t=99999999):
        super().__init__(t)
        self.seed_t=random.random()
        self.z_index=22
    def draww(self,screen):
        t = self.max_time-self.life_time+self.seed_t
        th = t*5*3.14
        r = 6
        pygame.draw.circle(screen,[177,177,177],[int(self.x+r*cos(th)),int(self.y+r*sin(th))],4)
        
class 吸血(model):
    def __init__(self,t=99999999):
        super().__init__(t)
        self.z_index=22
    def draww(self,screen):
        t = (self.max_time-self.life_time)*5
        color = (sin(t)*50+200,88,88)
        po1=(self.x-8,self.y-8)
        po2=(self.x+8,self.y+8)
        pygame.draw.line(screen,color,po1,po2,4)
        po1=(self.x+8,self.y-8)
        po2=(self.x-8,self.y+8)
        pygame.draw.line(screen,color,po1,po2,4)

def s(t):
    return (sin(t)+1)/2

class 持续施法(model):
    def __init__(self,t):
        super().__init__(t)
        self.z_index=22
    def draww(self,screen):
        t = (self.max_time-self.life_time)*20
        color = [255*s(t),255*s(t+3.14*2/3),255*s(t-3.14*2/3)]
        pygame.draw.circle(screen,color,[int(self.x),int(self.y)],21,3)
        
class 吟唱(model):
    def __init__(self,t=99999999):
        super().__init__(t)
        self.z_index=22
    def draww(self,screen):
        t = (self.max_time-self.life_time)*45
        line_n=30
        for i in range(0+int(t*200/321.8),line_n+int(t*200/321.8)):
            th = i*321.8
            r = th/200 -t
            r2 = r+13
            h=hash(str(int(th)))
            color = (h/136/136%136+120,h/136%136+120,h%136+120)
            x,y = (r*cos(th),r*sin(th))
            x2,y2 = (r2*cos(th),r2*sin(th))
            # print(x,y,x2,y2)
            pygame.draw.line(screen,color,(self.x+x,self.y+y),(self.x+x2,self.y+y2),2)

class 沉默(model):
    def __init__(self,t):
        super().__init__(t)
    def draww(self,screen):
        self.font = pygame.font.SysFont('SimHei', 20)
        self.font_surface = self.font.render('黙', True, (0,0,0))
        screen.blit(self.font_surface, (self.x+1, self.y+1))
        self.font_surface = self.font.render('黙', True, (255,255,255))
        screen.blit(self.font_surface, (self.x, self.y))
        
class 减速(model):
    def __init__(self,t):
        super().__init__(t)
    def draww(self,screen):
        self.font = pygame.font.SysFont('SimHei', 20)
        self.font_surface = self.font.render('减速', True, (0,0,0))
        screen.blit(self.font_surface, (self.x+1, self.y+1))
        self.font_surface = self.font.render('减速', True, (255,255,255))
        screen.blit(self.font_surface, (self.x, self.y))
        
class 血条(model):
    def __init__(self,t=99999999,color=(255,0,0)):
        super().__init__(t)
        self.color=color
        self.z_index=999
    def draww(self,screen):
        pygame.draw.rect(screen,(0,0,0), (self.x-19,self.y-28,36*(self.hp/self.maxhp),6))
        pygame.draw.rect(screen, self.color, (self.x-17,self.y-27,34*(self.hp/self.maxhp),4))
        
class 蓝条(model):
    def __init__(self,t=99999999):
        super().__init__(t)
        self.color=(133,133,255)
        self.z_index=999
    def draww(self,screen):
        pygame.draw.rect(screen,(0,0,0), (self.x-19,self.y-23,36*(self.mana/self.max_mana),6))
        pygame.draw.rect(screen, self.color, (self.x-17,self.y-22,34*(self.mana/self.max_mana),4))

class 减速光环(model):
    def __init__(self,r,t=99999999):
        super().__init__(t)
        self.r=r
        self.z_index=-10
    def draww(self,screen):
        pygame.draw.circle(screen,(255,255,255),[int(self.x),int(self.y)],self.r,3)
        t =(self.max_time-self.life_time)*3
        for i in range(3):
            t+=3.14*2/3
            pygame.draw.circle(screen,(255,255,255),[int(self.x),int(self.y)],int(self.r*(1+sin(t))/2+3),3)

class 火焰(model):
    def __init__(self,r,t=99999999):
        super().__init__(t)
        self.r=r
        self.z_index=-10
    def draww(self,screen):
        pygame.draw.circle(screen,[rd(100,255),55,55],[int(self.x),int(self.y)],self.r,3)
        for i in range(20):
            t=rdth()
            po1=[int(self.x+self.r*rdp()*cos(t)),int(self.y+self.r*rdp()*sin(t))]
            t=rdth()
            po2=[int(self.x+self.r*rdp()*cos(t)),int(self.y+self.r*rdp()*sin(t))]
            pygame.draw.line(screen,[rd(100,255),55,55],po1,po2,2)
        
class 扩散白圈(model):
    def __init__(self,r,t=99999999,reverse=False):
        super().__init__(t)
        self.r=r
        self.reverse=reverse
    def draww(self,screen):
        if self.reverse:
            n=self.life_time/self.max_time
        else:
            n=1-self.life_time/self.max_time
        pygame.draw.circle(screen,(255,255,255),[int(self.x),int(self.y)],good(self.r*n),3)
        
class 圆(model):
    def __init__(self,r,t=99999999,color=(255,255,255)):
        super().__init__(t)
        self.r=r
        self.color=color
        self.z_index=22
    def draww(self,screen):
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.r,3)
        
class 爆炸(model):
    def __init__(self,r,t=99999999,color=(255,100,100)):
        super().__init__(t)
        self.r=r
        self.color=color
    def draww(self,screen):
        r=int(self.r*(1-self.life_time/self.max_time)**0.5)
        r2=int(self.r*(1-self.life_time/self.max_time)**3)
        pygame.draw.circle(screen,self.color,[int(self.x),int(self.y)],r,min(r,abs(r-r2)))
        
class 火球(model):
    def __init__(self,t=99999999):
        super().__init__(t)
    def draww(self,screen):
        t=self.max_time-self.life_time
        r=int(14+2*sin(30*t))
        pygame.draw.circle(screen,[255,255,0],[int(self.x),int(self.y)],r)
        pygame.draw.circle(screen,[255,0,0],[int(self.x),int(self.y)],r+1)
        
        
def good(f):
    f=max(f,10)
    return int(f)
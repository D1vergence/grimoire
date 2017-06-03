import pygame
import magic
import model
from screen import screen
import ev
from tool import *
import effect

import random
rd = random.randint

unit_pool=unit_list()

class unit():
    def __init__(self):
        self.effect=my_list(self)
        self.magic =magic_list(self)
        self.model =my_list(self)
        self.name='basic_unit'
        self.v=vec(0,0)
        self.set_v(0,0)
        self.speed=10
        self.iki=True
        self.player=0
        self.maxhp=10
        self.hp=self.maxhp
        self.max_mana=400
        self.mana=self.max_mana 
        self.mana_rc=0          #回魔速度
        self.hp_rc=0            #回血速度
        self.die_model=None     #死亡时播放的模型
        self.now_cmd=('hold',None)
        self.face=vec(0,0)      #朝向
        self.size=-999          #碰撞体积
        self.offer_exp=0        #被击杀时提供经验
        self.exp=0              #现有经验
        
        
    def birth(self):
        pass
    #绘图
    def draw(self,screen):
        for i in self.model:
            i.draw(screen)
    #时间经过
    def time_pass(self,t):
        self.draw(screen)
        
        #每秒回复魔力
        self.mana=min(self.mana+t*self.mana_rc,self.max_mana)
        self.hp  =min(self.hp  +t*self.hp_rc  ,self.maxhp  )
        
        #自身行为经过
        if self.now_cmd[0]=='hold':
            pass
        elif self.now_cmd[0]=='move':
            pre_v=self.v
            v_tar=self.now_cmd[1]
            v=v_tar-self.v
            v.normalize()
            self.face=v
            go=v*t*self.get_speed()
            if go.mo()<(v_tar-self.v).mo():
                self.v+=go
            else:
                self.v=v_tar
            
            #碰撞体积
            for i in unit_pool:
                if i is self: continue
                d=(i.v-self.v).mo()
                min_d=self.size+i.size
                # print(d)
                if d<min_d:
                    if (i.v-pre_v).mo()>d:
                        # self.v=pre_v
                        temp=(i.v-self.v)
                        if temp==vec(0,0): 
                            temp=vec(rd(0,1)*2-1,rd(0,1)*2-1)
                        self.v=i.v-temp.normalize()*min_d
                        # break
            if self.v==v_tar: 
                self.cmd('hold')

        #效果和模型经过
        de(self.effect, lambda i: not i.iki)
        for i in self.effect:
            i.time_pass(t)
            
        de(self.model, lambda i: not i.iki)
        for i in self.model:
            i.time_pass(t)

        #魔法冷却经过
        for i in self.magic:
            i.time_pass(t)
            

    #发布指令(事件)
    #写法 cmd('干什么',*list)
    #         cmd(x,y) 默认是移动
    #         cmd(vec) 也可以把x,y用向量表示
    def cmd(self,*li):
        ev.ev(self,'_cmd',li)
    def _cmd(self,li):
        if type(li[0])!=str:
            li=('move',*li)
        
        s=li[0]
        if   s=='hold':
            self.now_cmd=('hold',None)
            
        elif s=='move': 
            if type(li[1])==vec:
                self.now_cmd=('move',li[1])
            else:
                self.now_cmd=('move',vec(li[1],li[2]))
                
        elif s=='cast':
            ev.ev(self,'_cast',li[1],li[2],li[3])
            
        else:
            raise BaseException('无法识别的命令')


    def imm(self):
        return any([isinstance(i,effect.magic_imm) for i in self.effect])
    #位移
    def set_v(self,x=0,y=0):
        if type(x)==vec:
            y=x.y
            x=x.x
        ev.ev(self,'_set_v',x,y)
    def _set_v(self,x,y):
        self.v.x=x
        self.v.y=y
        self.cmd('hold')

    #支付魔法
    def cost_mana(self,n):
        if self.mana>=n:
            self.mana-=n
            return True
        return False
        
    #获得速度 (事件)
    def get_speed(self):
        return ev.ev(self,'_get_attr','speed',self.speed).rep
        
    def _get_attr(self,*d):
        None
        #这是一个虚假方法，对属性值的处理在效果中已经全部结束了


    #添加效果(事件)
    def add_ef(self,ef):
        ev.ev(self,'_add_ef',ef)
    def _add_ef(self,ef):
        self.effect.append(ef)

    #施法命令(事件)
    def cast(self,magic,x,y):
        self.cmd('cast',magic,x,y)
    #中间会从cmd跳转一下
    def _cast(self,magic,x,y):
        magic.call(x,y)

    #单位死亡(事件)
    def die(self,damage=None):
        ev.ev(self,'_die',damage)
    def _die(self,damage):
        if not self.iki:
            return
        self.iki=False
        for i in self.effect:
            i.die()
        if self.die_model:
            tt=decorator(self.die_model)
            tt.set_v(self.v)
            unit_pool.append(tt)
        if damage:
            damage.source_unit.exp+=self.offer_exp     #token有鬼
            # print(damage.source.owner,'有',damage.source.owner.exp,'经验')
            tt=decorator(model.叮())
            tt.set_v(damage.source_unit.v)
            unit_pool.append(tt)
            
        
    #受到伤害(事件)
    def hurt(self,damage):
        ev.ev(self,'_hurt',damage)
    def _hurt(self,*d):
        pass
        
    #受到回复(事件)
    def heal(self,x=100):
        ev.ev(self,'_heal',x)
    def _heal(self,*d):
        pass

    #对目标造成伤害(事件)
    def dam(self,tar,damage):
        ev.ev(self,'_dam',tar,damage)
    def _dam(self,tar,damage):
        tar.hurt(damage)

#——————————————————————————————————————————
#——————————————————————————————————————————
#——————————————————————————————————————————
#——————————————————————————————————————————


class real_unit(unit):
    def __init__(self):
        super().__init__()
        self.size=15

    def birth(self):
        a=self.player
        if a==0:
            self.model.append(model.血条(color=(255,255,255)))
        elif a==1:
            self.model.append(model.血条(color=(255,0,0)))
        elif a==2:
            self.model.append(model.血条(color=(0,255,0)))
        else:
            color=(a//200//200%200+55,a//200%200+55,a%200+55)
            self.model.append(model.血条(color=color))    
            self.model.append(model.蓝条())    
            
            
    def _hurt(self,damage):
        self.hp-=damage.value
        if self.hp<=0:
            self.die(damage)
    def _heal(self,x):
        self.hp+=x
        if self.hp>self.maxhp:
            self.hp=self.maxhp

class sheep(real_unit):
    def __init__(self):
        super().__init__()
        self.model.append(model.圆形())
        self.add_ef(effect.go233())
        # self.add_ef(effect.limit_screen())
        self.speed=150
        self.maxhp=60
        self.hp=60
        self.die_model=model.圆形消失(0.6)
        
class soldier(real_unit):
    def __init__(self):
        super().__init__()
        self.model.append(model.圆形())
        self.speed=200
        self.maxhp=150
        self.hp=150
        self.die_model=model.圆形消失(0.8)
        self.add_ef(effect.funnel(r=100,speed=350,cd=1.2,power=10))
        self.add_ef(effect.closing())
        self.offer_exp=40+rd(0,10)

class abst_unit(unit):
    def __init__(self):
        super().__init__()
        self.add_ef(effect.magic_imm())
        
class stone(abst_unit):
    def __init__(self,r=30):
        super().__init__()
        self.size=r
        self.model.append(model.石(r=r,color=(111,111,111)))
    
    
        
class token(abst_unit):
    def __init__(self):
        super().__init__()

class decorator(abst_unit):
    def __init__(self,model):
        super().__init__()
        self.model.append(model)
    def time_pass(self,t):
        abst_unit.time_pass(self,t)
        if len(self.model)==0: 
            self.die()

#箭矢
class arrow(token):
    def __init__(self):
        super().__init__()
        self.speed=300

#指向单位的箭矢
class arrow_to_u(arrow):
    def __init__(self,tar,act=lambda:0,set_model=None,retent=False):
        super().__init__()
        if not set_model:
            set_model = model.晕眩()
        self.model.append(set_model)
        self.tar=tar
        self.act=act
        self.retent=retent
    def time_pass(self,time):
        arrow.time_pass(self,time)
        self.cmd(self.tar.v.x,self.tar.v.y)
        if (self.tar.v-self.v).mo()<10 and not self.retent:
            self.act()
            self.die()
            
#指定向量的箭矢
class arrow_to_d(arrow):
    def __init__(self,v,set_model=None,exact=False):
        super().__init__()
        self.speed=400
        if not set_model:
            set_model = model.箭头()
        self.model.append(set_model)
        self.add_ef(effect.kill_out_screen())
        self.p_v=v
        self.die_model=model.爆炸(80,0.2)
        self.exact=exact
    
    def birth(self):
        self.tar_v=self.v+self.p_v

    def time_pass(self,time):
        arrow.time_pass(self,time)
        self.cmd(self.v+self.p_v*999)
        if self.exact and (self.tar_v-self.v).mo()<10:
            self.die()


class ship(real_unit):
    def __init__(self):
        super().__init__()
        self.speed=110
        self.maxhp=250
        self.hp=250
        self.model.append(model.方块(r=24))
        self.add_ef(effect.funnel())
        self.add_ef(effect.go233(r=1000,expect=2))
        # self.add_ef(effect.limit_screen())
        self.die_model=model.爆炸(r=70,t=0.4)
        
class pacifier(real_unit):
    def __init__(self):
        super().__init__()
        self.speed=0
        self.maxhp=300
        self.hp=300
        self.model.append(model.方块(r=20))
        m=magic.平定者攻击()
        self.magic.append(m)
        self.add_ef(effect.auto_cast( magic=m ))
        self.die_model=model.爆炸(r=70,t=0.4)

class tower(real_unit):
    def __init__(self):
        super().__init__()
        self.size=50
        self.speed=0
        self.maxhp=1000
        self.hp=1000
        self.model.append(model.圆形(r=50))
        self.add_ef(effect.funnel(r=400,cd=1,power=50,arrow_model=model.火球))
        self.die_model=model.爆炸(r=100,t=0.8)
        self.add_ef(effect.magic_imm())

#神风
class kamikaze(arrow_to_d, real_unit):
    def __init__(self,v):
        super().__init__(v,set_model=model.神风(),exact=True)
        self.speed=600
        self.maxhp=25
        self.hp=25
        self.size=-999
        de(self.effect,lambda x: type(x)==effect.magic_imm)     #神风并不是魔免的
        self.add_ef(effect.funnel(arrow_model=lambda:model.直线(width=1),speed=550,cd=0.2,power=2))
        self.add_ef(effect.bomb(r=-1,power=8, aoe=True, aoe_r=121))
    def birth(self):
        arrow_to_d.birth(self)
        real_unit.birth(self)
        
        
        


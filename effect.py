﻿import pygame
import random
rd = random.randint
from tool import *
import model
import unit
import ev
import damage
import fantasy
from screen import screen

#基础效果
class effect(fantasy.fantasy):
    def __init__(self,life_time=99999999):
        self.max_time=life_time
        self.life_time=life_time
        self.iki=True
        self.ignore_imm=False
        self.source=None
        self.model=[]
    def birth(self):
        None
    def time_pass(self,time):
        self.draw(screen)
        self.life_time-=time
        if self.life_time<=0:
            self.die()
        for i in self.model:
            i.time_pass(time)
            if not i.iki:
                self.model.remove(i)
    def draw(self,screen):
        for i in self.model:
            i.draw(screen)
    def die(self):
        self.iki=False
    def set_owner(self,owner):
        self.owner=owner
        for i in self.model:
            i.owner=self.owner
    def change(self,e):
        return e

#火焰缠绕
class fire(effect):
    def __init__(self,life_time=9999999,r=30,power=10,ali_dam=True):
        super().__init__(life_time)
        self.ignore_imm=True    #注意，光环效果本身当然无视魔免，但是光环施加的效果不一定
        self.hurt_per_s = power
        self.hurt_distance = r
        self.ali_dam=ali_dam
        self.model.append(model.火焰(r))
        self.model.append(model.白圆(r*1.2,t=0.2))
        
    def time_pass(self,time):
        effect.time_pass(self,time)
        for i in unit.unit_pool:
            if i is self.owner:
                continue
            if not self.ali_dam and i.player==self.owner.player:
                continue
            if (i.v-self.owner.v).mo()<self.hurt_distance:
                self.dam(i,time*self.hurt_per_s)
                
#对碰到的单位仅造成一次伤害
class one_dam(effect):
    def __init__(self,life_time=9999999,r=30,power=50):
        super().__init__(life_time)
        self.ignore_imm=True
        self.power = power
        self.r=r
        self.hurted_pool=[]
        
    def time_pass(self,time):
        effect.time_pass(self,time)
        for i in unit.unit_pool:
            if i.player==self.owner.player:
                continue
            if i in self.hurted_pool:
                continue
            if (i.v-self.owner.v).mo()<self.r:
                self.dam(i,self.power)
                self.hurted_pool.append(i)
                

#为单位施加效果的光环 (统一的)        
class aura(effect):
    def __init__(self,life_time=9999999,r=30,ali_dam=True,generator=None):
        super().__init__(life_time)
        self.ignore_imm=True    #注意，光环效果本身当然无视魔免，但是光环施加的效果不一定
        self.r = r
        self.ali_dam=ali_dam
        self.model.append(model.减速光环(r=r))
        if generator:
            self.generator = generator
        else:
            self.generator = lambda : slow(life_time=0,percent=0.7)
            
    def time_pass(self,time):
        effect.time_pass(self,time)
        for i in unit.unit_pool:
            if not self.ali_dam and i.player==self.owner.player:
                continue
            if (i.v-self.owner.v).mo()<self.r:
                e=self.generator()
                e.source=self
                ev.ev(i,'_add_ef',e)

#减速
class slow(effect):
    def __init__(self,life_time=99999999,percent=0.1):
        super().__init__(life_time)
        self.model.append(model.减速(life_time))
        self.percent=percent
    def change(self,event):
        if event.kind=='_get_attr' and event.arg[0]=='speed':
            event.arg[1]*=self.percent
        return event
    def __repr__(self):
        return str(self.life_time)
        
#沉默
class silence(effect):
    def __init__(self,life_time=99999999):
        super().__init__(life_time)
        self.model.append(model.沉默(life_time))
    def birth(self):
        for i in self.owner.effect:
            if type(i)==song:
                i.die(normal=False)
    def change(self,event):
        if event.kind=='_cast':
            return None
        else:
            return event
            
#吸血
class vampire(effect):
    def __init__(self,life_time=99999999):
        super().__init__(life_time)
        self.model.append(model.吸血(life_time))
    def change(self,event):
        if event.kind=='_dam':
            self.owner.heal(self.owner,event.arg[1]*0.5)
        return event
        
#倒计时死亡(用于召唤生物)
class kill_pass_time(effect):
    def __init__(self,life_time):
        super().__init__(life_time)
        self.ignore_imm=True
        self.model.append(model.倒计时(life_time))
    def die(self):
        self.owner.die()
        effect.die(self)

#晕眩
class stun(effect):
    def __init__(self,t):
        super().__init__(t)
        self.model.append(model.晕眩(t))
    def birth(self):
        self.owner.cmd('hold')
    def change(self,event):
        if event.kind=='_cmd':
            return None
        return event

#强制移动
class forced_move(effect):
    def __init__(self,x=0,y=0,t=99999999):
        super().__init__(t)
        self.v_tar=vec(x,y)
        self.speed=1300
    def time_pass(self,t):
        effect.time_pass(self,t)
        v=self.v_tar-self.owner.v
        v.normalize()
        go=v*t*self.speed
        if go.mo()>(self.v_tar-self.owner.v).mo():
            self.owner.v=self.v_tar
            self.die()
        else:
            self.owner.v+=go
    def change(self,event):
        if event.kind=='_cmd':
            return None
        return event

#吟唱
class song(effect):
    def __init__(self,life_time,function):
        super().__init__(life_time)
        self.ignore_imm=True
        self.model.append(model.吟唱(life_time))
        self.f=function
    def die(self,normal=True):
        if normal:
            self.f()
        effect.die(self)
    def change(self,event):
        if event.kind=='_cmd':
            self.die(normal=False)
            return event
        return event
        
#持续施法
class continue_cast(effect):
    def __init__(self,t,die_func):
        super().__init__(t)
        self.ignore_imm=True
        self.model.append(model.持续施法(t))
        self.f=die_func
    def die(self):
        self.f()
        effect.die(self)
    def change(self,event):
        if event.kind=='_cmd':
            self.die()
        return event
        
        

#离开屏幕后移除
class kill_out_screen(effect):
    def __init__(self):
        super().__init__()
        self.ignore_imm=True

    def time_pass(self,time):
        effect.time_pass(self,time)
        if not -200<self.owner.v.y<1000:
            self.owner.die()
        if not -200<self.owner.v.x<1600:
            self.owner.die()

#不能离开屏幕
class limit_screen(effect):
    def __init__(self):
        super().__init__()
        self.ignore_imm=True

    def time_pass(self,time):
        effect.time_pass(self,time)
        self.owner.v.x=limit(self.owner.v.x,10,1356)
        self.owner.v.y=limit(self.owner.v.y,10,758)

#走来走去233333
class go233(effect):
    def __init__(self,expect=1,r=100):
        super().__init__()
        self.ignore_imm=True
        self.expect=expect
        self.r=r

    def time_pass(self,time):
        if random.random()<time*self.expect:
            self.owner.cmd(self.owner.v.x+rd(-self.r,self.r),self.owner.v.y+rd(-self.r,self.r))

#效果免疫(其实实际上只免疫effect)
class magic_imm(effect):
    def __init__(self):
        super().__init__()
        self.ignore_imm=True
    def birth(self):
        for i in self.owner.effect:
            if not i.ignore_imm:
                i.die()
    def change(self,event):
        if event.kind=='_add_ef' and not event.arg[0].ignore_imm:
            return None
        else:
            return event

#伤害免疫
class dam_imm(effect):
    def __init__(self,t=9999999):
        super().__init__(t)
        self.ignore_imm=True
        self.model.append(model.圆(r=25,color=(255,255,0)))
    def change(self,event):
        if event.kind=='_hurt':
            return None
        return event
    
#单位生成器
class unit_gen(effect):
    def __init__(self,t=9999999,cd=0.5,unit=lambda:0):
        super().__init__(t)
        self.ignore_imm=True
        self.cd=cd
        self.cd_left=0
        self.unit=unit
    def time_pass(self,t):
        effect.time_pass(self,t)
        self.cd_left-=t
        if self.cd_left<0:
            self.cd_left+=self.cd
            self.summon(self.unit())

#浮游炮
class funnel(unit_gen):
    def __init__(self,life_time=9999999,r=200):
        self.r = r
        def gen():
            tar_pool=list(filter(lambda i: i.player!=self.owner.player 
                                    and isinstance(i,unit.real_unit)
                                    and (i.v-self.owner.v).mo()<self.r
                        , unit.unit_pool))
            if tar_pool:
                def d(i):
                    return lambda:self.dam(i,10)
                i=random.choice(tar_pool)
                t=unit.arrow_to_u(i,act=d(i))
                t.die_model=model.爆炸(20,0.2)
                return t
        super().__init__(life_time,cd=0.5,unit=gen)

#對臨近單位自爆
class bomb(effect):
    def __init__(self,life_time=9999999,r=200,power=30,aoe=False,aoe_r=400):
        super().__init__(life_time)
        self.r = r
        self.power = power
        self.ignore_imm=True
        self.aoe=aoe
        self.aoe_r=aoe_r
    def time_pass(self,t):
        effect.time_pass(self,t)
        for i in unit.unit_pool:
            if i.player==self.owner.player or not isinstance(i,unit.real_unit):
                continue
            if (i.v-self.owner.v).mo()<self.r:
                if not self.aoe:
                    self.dam(i,self.power)
                self.owner.die()
                return
    def die(self):
        if self.aoe:
            for i in unit.unit_pool:
                if (self.owner.v-i.v).mo()<self.aoe_r:
                    self.dam(i,self.power)
        effect.die(self)

#自动靠近敌人
class closing(effect):
    def __init__(self,t=9999999):
        super().__init__(t)
        self.ignore_imm=True
    def time_pass(self,t):
        effect.time_pass(self,t)
        tar_pool=list(filter(lambda i: i.player!=self.owner.player 
                                    and isinstance(i,unit.real_unit)
                        , unit.unit_pool))
        if tar_pool:
            self.owner.cmd(min(tar_pool,key= lambda i: (i.v-self.owner.v).mo()).v )

#吞噬
class eat(effect):
    def __init__(self,t=9999999,eat_unit=None):
        super().__init__(t)
        self.ignore_imm=True
        self.eat_unit=eat_unit
        # print(eat_unit.__class__.__name__)
        unit.unit_pool.remove(self.eat_unit)
    def die(self):
        self.eat_unit.set_v(self.owner.v)
        unit.unit_pool.append(self.eat_unit)
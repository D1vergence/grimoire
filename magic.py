import pygame
import random
rd = random.randint
from tool import *
import unit
import effect
import model

class magic():
    def __init__(self):
        self.song_time=3
        self.cost=100
        self.cool_down=5
        self.cool_down_left=0
    def call(self,x,y):
        if self.cool_down_left: return
        self.owner.cmd('hold')
        if self.owner.cost_mana(self.cost):
            self.cool_down_left=self.cool_down
            self.owner.add_ef(effect.song(self.song_time,lambda: self.act(x,y)))
    def time_pass(self,t):
        self.cool_down_left-=t
        if self.cool_down_left<0:
            self.cool_down_left=0
    def act(self,x,y):
        pass

        
class 冲击波(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.1
    def act(self,x,y):
        t=self.owner.summon(unit.arrow_to_d(x-self.owner.v.x,y-self.owner.v.y))
        t.add_ef(effect.one_dam(r=30,power=50))


class 火风暴(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.1
    def act(self,x,y):
        t=self.owner.summon(unit.token(),2,x,y)
        t.add_ef(effect.fire(r=100))


class 冰风暴(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
    def act(self,x,y):
        t=self.owner.summon(unit.token(),8,x,y)
        t.add_ef(effect.aura(r=100, generator=lambda: effect.slow(life_time=0,percent=0.7)))

class 召唤舰队(magic):
    def __init__(self):
        super().__init__()
        self.song_time=1.3
        self.cool_down=18
    def act(self,x,y):
        for i in range(0,4):
            self.owner.summon(unit.ship(),9,self.owner.v.x+100*(i//2-0.5),self.owner.v.y+100*(i%2-0.5))
        
class 暗影冲锋(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.3
        self.cool_time=7
    def act(self,x,y):
        self.owner.add_ef(effect.forced_move(x,y))

class 绿色原谅光线(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
        self.r=60
        self.cool_down=6
    def act(self,x,y):
        self.owner.summon(unit.decorator(model.激光(color=(125,255,125),t=0.2,pos=(x,y),r=self.r*2)))
        x1=self.owner.v.x; y1=self.owner.v.y; x2=x; y2=y;
        a=y2-y1
        b=x1-x2
        c=(y1-y2)*x1+(x2-x1)*y1
        for i in unit.unit_pool:
            d=abs(a*i.v.x+b*i.v.y+c)/(a*a+b*b)**0.5
            if i is not self.owner and d<self.r and vec(x2-x1,y2-y1)*(i.v-self.owner.v)>0:
                self.owner.dam(i,50)

#这名字超级随便的我自己都笑了23333                
class 射炸弹(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
        self.r=60
        self.cool_down=1
    def act(self,x,y):
        t=self.owner.summon(unit.arrow_to_d(x-self.owner.v.x,y-self.owner.v.y))
        t.die_model=model.爆炸(t=0.3,r=200)
        t.speed=1000
        t.add_ef(effect.bomb(r=30,power=100,aoe=True,aoe_r=200))
        

class 沉默风暴(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
    def act(self,x,y):
        t=self.owner.summon(unit.token(),4,x,y)
        t.add_ef(effect.aura(r=140, generator=lambda: effect.silence(life_time=0)))
        
class 闪现(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.3
        self.cool_down=12
    def act(self,x,y):
        self.owner.set_v(x,y)
        self.owner.summon(unit.decorator(model.闪光(0.5)))
        
class 净化光线(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.8
        self.cost=150
        self.cool_down=4
    def act(self,x,y):
        t=self.owner.summon(unit.token())
        t.speed=160
        t.add_ef(effect.fire(r=144,power=200,ali_dam=False))
        t.add_ef(effect.closing())
        self.owner.add_ef(effect.continue_cast(t=30,die_func=lambda: t.die()))

class 气球炸弹(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
        self.cost=150
        self.cool_down=4
    def act(self,x,y):
        def unit_gen():
            t=unit.token()
            t.speed=80
            t.model.append(model.火球())
            t.die_model=model.爆炸(t=0.2,r=50)
            t.add_ef(effect.bomb(r=30,power=40))
            t.add_ef(effect.closing())
            return t
        self.owner.add_ef(effect.unit_gen(t=3,cd=0.4,unit=unit_gen))

class 战争践踏(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.4
    def act(self,x=0,y=0):
        r=180
        for i in unit.unit_pool:
            if i is not self.owner and (self.owner.v-i.v).mo()<r:
                self.owner.dam(i,30)
                i.add_ef(effect.slow(life_time=1.4,percent=0.25))
        self.owner.model.append(model.白圆(r,0.15))
        self.owner.model.append(model.白圆(r,0.2))
        self.owner.model.append(model.白圆(r,0.25))

class 闪电(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.1
        self.cool_down=4
        self.cost=80
    def act(self,x=0,y=0):
        def d(i):
            def g():
                self.owner.dam(i,80)
            return g
        r=300

        tar_pool=list(filter(lambda i: i.player!=self.owner.player 
                                    and isinstance(i,unit.real_unit)
                                    and (self.owner.v-i.v).mo()<r
                        , unit.unit_pool))
        if tar_pool:
            i=random.choice(tar_pool)
            self.owner.dam(i,80)
            self.owner.summon(unit.decorator(model.闪电(t=0.2,tar=i.v)))

class 射箭(magic):
    def __init__(self):
        super().__init__()
        self.cost=50
        self.song_time=0.1
        self.cool_down=1.3
    def act(self,x,y):
        t=self.owner.summon(unit.arrow_to_d(x-self.owner.v.x,y-self.owner.v.y))
        t.add_ef(effect.bomb(r=30,power=30))

if __name__=='__main__':
    pass
import pygame
import random
rd = random.randint
from tool import *
import unit
import effect
import model
import damage
import fantasy
from math import sin ,cos

class magic(fantasy.fantasy):
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
        self.name='「冲击波」'
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v))
        t.add_ef(effect.one_dam(r=30,power=50))

class 烈焰风暴(magic):
    def __init__(self):
        super().__init__()
        self.name='火焰「烈焰风暴」'
        self.song_time=0.4
        self.cost=80
        self.cool_down=2.9
    def act(self,x,y):
        t=self.summon(unit.token(),1,x,y)
        t.add_ef(effect.fire(r=100,power=100))

class 冰风暴(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.5
    def act(self,x,y):
        t=self.summon(unit.token(),8,x,y)
        t.add_ef(effect.aura(r=100, generator=lambda: effect.slow(life_time=0,percent=0.7)))

class 舰队(magic):
    def __init__(self):
        super().__init__()
        self.name='「舰队已经抵达」'
        self.song_time=1.3
        self.cool_down=18
    def act(self,x,y):
        for i in range(0,9):
            th=2*3.14/9*i
            self.summon(unit.ship(),9+random.random(),self.owner.v.x+100*cos(th),self.owner.v.y+100*sin(th))
        
class 暗影冲锋(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.3
        self.cool_time=7
    def act(self,x,y):
        self.owner.add_ef(effect.forced_move(x,y))

class 原谅光线(magic):
    def __init__(self):
        super().__init__()
        self.name='「原谅光线」'
        self.song_time=0.3
        self.r=20
        self.cool_down=2.3
        self.cost=80
        self.power=40

    def act(self,x,y):
        self.summon(unit.decorator(model.激光(color=(125,255,125),t=0.2,pos=(x,y),r=self.r*2)))
        for i in self.sel_line(self.owner.v,vec(x,y)):
            if i is not self.owner: 
                i.add_ef(effect.slow(life_time=0.7,percent=0.4))
                self.dam(i,self.power)
                
                

#我自己都笑了23333
class 若风一指(magic):
    def __init__(self):
        super().__init__()
        self.name='若风「须臾的圣枪」'
        self.song_time=0.5
        self.r=60
        self.cool_down=1
    def act(self,x,y):
        v=vec(x-self.owner.v.x, y-self.owner.v.y).adjust_angle((random.random()-0.5)/2)
        t=self.summon(unit.arrow_to_d(v,set_model=model.箭头(l=50,width=6,color=(255,111,111))))
        t.die_model=model.爆炸(t=0.3,r=200)
        t.speed=1200
        t.add_ef(effect.bomb(r=45,power=100,aoe=True,aoe_r=200))

#集めた言葉も、土の中に朽ちるだけ
class 沉默风暴(magic):
    def __init__(self):
        super().__init__()
        self.name='循环「言语腐朽的土」'
        self.song_time=0.5
        self.cost=100
        self.cool_down=5
    def act(self,x,y):
        r=155
        t=self.summon(unit.token(),7,x,y)
        t.add_ef(effect.aura(r=r, color=(50,150,0), generator=lambda: effect.silence(life_time=0) ))
        t.add_ef(effect.aura(r=r, color=(50,150,0), generator=lambda i: effect.slow(percent=0.4+0.4*((t.v-i.v).mo()/r),life_time=0) ))

class 闪现(magic):
    def __init__(self):
        super().__init__()
        self.name='「折跃」'
        self.song_time=0.3
        self.cool_down=12
    def act(self,x,y):
        self.owner.set_v(x,y)
        self.summon(unit.decorator(model.闪光(0.5)))


class 净化光线(magic):
    def __init__(self):
        super().__init__()
        self.name='净化「净化光线」'
        self.song_time=0.8
        self.cost=150
        self.cool_down=4
    def act(self,x,y):
        t=self.summon(unit.token())
        t.speed=160
        t.add_ef(effect.fire(r=144,power=200,ali_dam=False))
        t.add_ef(effect.closing())
        self.owner.add_ef(effect.continue_cast(t=30,die_func=lambda: t.die()))


class 战争践踏(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.4
        self.name='「战争践踏」'
    def act(self,x=0,y=0):
        r=180
        for i in unit.unit_pool:
            if i is not self.owner and (self.owner.v-i.v).mo()<r:
                self.dam(i,30)
                i.add_ef(effect.slow(life_time=1.4,percent=0.25))
        self.owner.model.append(model.白圆(r,0.15))
        self.owner.model.append(model.白圆(r,0.2))
        self.owner.model.append(model.白圆(r,0.25))


class 闪电(magic):
    def __init__(self):
        super().__init__()
        self.name='「不稳定电流」'
        self.song_time=0.1
        self.cool_down=4
        self.cost=80
    def act(self,x=0,y=0):
        def d(i):
            def g():
                self.dam(i,80)
            return g
        r=300

        tar_pool=list(filter(lambda i: i.player!=self.owner.player 
                                    and isinstance(i,unit.real_unit)
                                    and (self.owner.v-i.v).mo()<r
                        , unit.unit_pool))
        if tar_pool:
            i=random.choice(tar_pool)
            self.dam(i,80)
            self.summon(unit.decorator(model.闪电(t=0.2,tar=i.v)))


class 光之矢(magic):
    def __init__(self):
        super().__init__()
        self.cost=35
        self.name='「光之矢」'
        self.song_time=0
        self.cool_down=1
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v))
        t.speed=600
        t.add_ef(effect.bomb(r=30,power=30))


class 冰之矢(magic):
    def __init__(self):
        super().__init__()
        self.cost=100
        self.name='「冰之矢」'
        self.song_time=0.3
        self.cool_down=7
    def act(self,x,y):
        v=vec(x,y)
        for i in range(-3,4):
            vi=(v-self.owner.v).adjust_angle(i*0.17)
            
            t=self.summon(unit.arrow_to_d(vi, model.箭头(color=(170,170,255))))
            t.die_model=model.爆炸(r=35,t=0.2,color=(200,180,255))
            t.speed=600
            t.add_ef(effect.bomb(r=30,power=30,func=lambda u:u.add_ef(effect.slow(life_time=2,percent=0.6))))


#233333
class 虚伪的磐舟(magic):
    def __init__(self):
        super().__init__()
        self.name='「虚伪的磐舟」'
        self.song_time=0.2
        self.cost=150
        self.cool_down=8
    def act(self,x,y):
        def unit_gen():
            v=(vec(x,y)-self.owner.v).adjust_angle(random.gauss(0,0.14))
            t=unit.arrow_to_d(v,model.箭头(l=15,color=(255,255,200),width=2))
            t.add_ef(effect.bomb(r=25,power=30))
            t.speed=500
            return t
        e=effect.unit_gen(cd=0.1,unit=unit_gen)
        self.owner.add_ef(e)
        self.owner.add_ef(effect.continue_cast(t=7,die_func=lambda: e.die()))

#咕噜咕噜？
class 星河漩涡(magic):
    def __init__(self):
        super().__init__()
        self.name='黑洞「星河漩涡」'
        self.song_time=0.8
        self.cost=150
        self.cool_down=15
        self.r=200
    def act(self,x,y):
        t=self.summon(unit.token(),2.3,x,y)
        t.model.append(model.吟唱())
        self.summon(unit.decorator(model=model.扩散白圈(t=0.3,r=self.r,reverse=True)),x=x,y=y)
        tar_pool=list(filter(lambda i: isinstance(i,unit.real_unit)
                                    and (t.v-i.v).mo()<self.r
                        , unit.unit_pool))
        for i in tar_pool:
            t.add_ef(effect.eat(eat_unit=i))

#最后的冬天，游行已经开始了。
#把被罪业玷污的街道净化吧。
class ghost_parade(magic):
    def __init__(self):
        super().__init__()
        self.name='春分「Ghost Parade」'
        self.song_time=1
        self.cost=140
        self.cool_down=50
        self.last_time=22
    def act(self,x,y):
        self.owner.add_ef(effect.slow(life_time=self.last_time,percent=0.5))
        for i in range(27):
            t=self.summon(unit.token(),self.last_time)
            t.speed=150
            t.add_ef(effect.fire(r=45,power=30,ali_dam=False))
            t.add_ef(effect.go666(center_unit=self.owner, r=400))

#潘大爷将携带大量炸药因意外事故掉落的在莆田理工大学空间站工作的学生从轨道高空投放，对敌人进行精确打击2333333
class 轨道坠落(magic):
    def __init__(self):
        super().__init__()
        self.name='星落「超级意外事故攻击」'
        self.song_time=0.2
        self.cost=1
        self.cool_down=3
        self.last_time=2
    def act(self,x,y):
        t=self.summon(unit.token(),x=x,y=y)
        t.die_model=model.爆炸(t=0.2,r=144)
        t.add_ef(effect.timer(t=2, func=t.die ))
        t.add_ef(effect.bomb(r=-1,power=80,aoe=True,aoe_r=144))
        
#Fire the EMT!!?
class 断电导弹(magic):
    def __init__(self):
        super().__init__()
        self.name='EMP「断电导弹」'
        self.song_time=0.2
        self.cost=1
        self.cool_down=3
        self.r=144
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v,exact=True,set_model=model.直线(width=10)))
        t.speed=500
        t.die_model=(model.爆炸(t=0.2,r=self.r,color=(255,255,255)))
        t.add_ef(effect.bomb(r=-1,power=0, aoe=True, aoe_r=self.r, func=lambda i:i.add_ef(effect.stun(2))))

#咚！
class 气球炸弹(magic):
    def __init__(self):
        super().__init__()
        self.name='气球「飞行的死」'
        self.song_time=0.2
        self.cost=150
        self.cool_down=7
    def act(self,x,y):
        def unit_gen():
            t=unit.token()
            t.speed=80
            t.model.append(model.火球())
            t.die_model=model.爆炸(t=0.2,r=50)
            t.add_ef(effect.bomb(r=30,power=40))
            t.add_ef(effect.closing())
            return t
        self.owner.add_ef(effect.unit_gen(t=6,cd=0.4,unit=unit_gen))

#潘大爷与一条直线上的pannx用户连线，向他们传送亚〇娜的本子，使他们在欲望的驱使下以极大的速度向潘大爷靠近。
#之所以对所有的单位都有效是因为panux是开源的23333
class panux连线(magic):
    def __init__(self):
        super().__init__()
        self.name='「Panux连线」'
        self.song_time=0.5
        self.cost=80
        self.cool_down=15
        self.r=60
    def act(self,x,y):
        self.summon(unit.decorator(model.激光(color=(125,125,125),t=0.4,pos=(x,y),r=self.r*2)))
        for i in self.sel_line(self.owner.v,vec(x,y)):
            if i is not self.owner: 
                i.add_ef(effect.forced_move(self.owner.v.x,self.owner.v.y))
    
if __name__=='__main__':
    pass
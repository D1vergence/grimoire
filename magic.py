import pygame
import random
import inspect
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
        self.song_time=3        #吟唱时间
        self.cost=100           #魔法消耗
        self.cool_down=5        #冷却时间
        self.cool_down_left=0   #当前冷却时间
        self.ran=400            #施法距离
        self.key=None           #默认快捷键
        
    def call(self,x,y):
        args = inspect.getargspec(self.act)[0]
        if len(args)==1:
            self._call()
        else:
            if (vec(x,y)-self.owner.v).mo()>self.ran: 
                return
            if args[1]=='target':
                v=vec(x,y)
                tar_pool=list(filter(lambda i: isinstance(i,unit.real_unit)
                                            and (i.v-v).mo()<50
                                , unit.unit_pool))
                if tar_pool:
                    target=min(unit.unit_pool,key = lambda x:(x.v-v).mo())
                    self._call(target)
            else:
                self._call(x,y)
        
    def _call(self,*d):
        if self.cool_down_left: return
        self.owner.cmd('hold')
        if self.owner.cost_mana(self.cost):
            self.cool_down_left=self.cool_down
            self.owner.add_ef(effect.song(self.song_time,lambda: self.act(*d)))
            
    def time_pass(self,t):
        self.cool_down_left-=t
        if self.cool_down_left<0:
            self.cool_down_left=0
    def act(self,*d):
        pass
        
class 攻击(magic):
    def __init__(self):
        super().__init__()
        self.cool_down=1.2
        self.song_time=0
        self.cost=0
        self.name='「普通攻击」'
        self.ran=300
        self.key='a'
    def act(self,target):
        t=self.summon(unit.arrow_to_u(target,act=lambda:self.dam(target,25),set_model=model.直线()))
        t.speed=800
        
class 部署平定者(magic):
    def __init__(self):
        super().__init__()
        self.cool_down=30
        self.song_time=1.1
        self.cost=120
        self.ran=300
    def act(self,x,y):
        self.summon(unit.pacifier(),25,x,y)
    
class 平定者攻击(magic):
    def __init__(self):
        super().__init__()
        self.cool_down=4.5
        self.song_time=0
        self.cost=0
        self.ran=800
        self.delay=2
        self.r=50
        self.power=30
    def act(self,target):
        x,y=(target.v.x,target.v.y)
        self.summon(unit.decorator(model.圆(r=self.r,t=self.delay)),t=None,x=x,y=y)
        def f():
            def unit_gen():
                t=self.summon(unit.arrow_to_d(vec(x+rd(-self.r//4*3,self.r//4*3),y+rd(-self.r//4*3,self.r//4*3))-self.owner.v,set_model=model.直线(width=1),exact=True))
                t.speed=350
                t.add_ef(effect.bomb(aoe=True,r=-1,aoe_r=self.r/4*3,power=self.power))
                return t
            self.owner.add_ef(effect.unit_gen(t=0.75,cd=0.15,unit=unit_gen))
        self.owner.add_ef(effect.timer(self.delay,f))
        
class 冲击波(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.1
        self.name='「冲击波」'
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v))
        t.add_ef(effect.one_dam(r=30,power=50))

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
            self.summon(unit.ship(),9+random.random()*1.5,self.owner.v.x+100*cos(th),self.owner.v.y+100*sin(th))
        
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

#焚书以始、焚人以终
class 烈焰风暴(magic):
    def __init__(self):
        super().__init__()
        self.name='火焰「幻书的星火」'
        self.song_time=0.1
        self.cost=50
        self.cool_down=8
        self.r=80
        self.power=120
        self.last_time=0.6
        self.ran=600
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v,set_model=model.圆形(r=10),exact=True))
        t.speed=400
        def f():
            t=self.summon(unit.token(),self.last_time,x,y)
            t.add_ef(effect.fire(r=self.r,power=self.power))
        t.add_ef(effect.bomb(r=-1,self_func=f ))
        
class 焚己以终(烈焰风暴):
    def __init__(self):
        super().__init__()
        self.name='净化「焚己以终」'
        self.song_time=0
        self.cost=35
        self.cool_down=0.5
        self.r=100
        self.power=120
        self.last_time=1
        self.ran=800
    def act(self,x,y):
        self.dam(self.owner,50)
        烈焰风暴.act(self,x,y)

class 纸上城壁(magic):
    def __init__(self):
        super().__init__()
        self.name='循环「纸上之物的城壁」'
        self.song_time=0
        self.cost=15
        self.cool_down=6
    def act(self):
        e=effect.dam_imm()
        self.owner.add_ef(e)
        self.owner.add_ef(effect.continue_cast(t=3,die_func=lambda: e.die()))

        
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
        
class 死者的叹息(magic):
    def __init__(self):
        super().__init__()
        self.name='「死者的叹息」'
        self.song_time=0.2
        self.cool_down=5
        self.cost=100
        self.ran=600
    def act(self,x,y):
        t=self.summon(unit.arrow_to_d(vec(x,y)-self.owner.v))
        t.speed=250
        t.add_ef(effect.grav(r=225,power=200))
        
class 紫水晶的叹息(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.2
        self.cool_down=4
        self.name='「紫水晶的叹息」'
    def act(self):
        self.owner.add_ef(effect.grav(4,r=225,power=-155))

#最后的冬天，游行已经开始了。
#把被罪业玷污的街道净化吧。
class ghost_parade(magic):
    def __init__(self):
        super().__init__()
        self.name='春分「Ghost Parade」'
        self.song_time=1
        self.cost=140
        self.cool_down=50
        self.last_time=20
    def act(self):
        # self.owner.add_ef(effect.slow(life_time=self.last_time,percent=0.5))
        mg=self.owner.magic
        q=mg.replace('q',焚己以终())
        w=mg.replace('w',沉默风暴())
        e=mg.replace('e',紫水晶的叹息())
        def f():
            mg.replace('q',q)
            mg.replace('w',w)
            mg.replace('e',e)
        self.owner.add_ef(effect.timer(self.last_time,f))
        for i in range(5):
            t=self.summon(unit.token(),self.last_time)
            t.speed=150
            t.add_ef(effect.fire(r=66,power=100,ali_dam=False))
            t.add_ef(effect.go666(center_unit=self.owner, r=300))


class 暗影冲锋(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.3
        self.cool_time=7
    def act(self,x,y):
        self.owner.add_ef(effect.forced_move(x,y))
        

class 闪现(magic):
    def __init__(self):
        super().__init__()
        self.name='「折跃」'
        self.song_time=0.3
        self.cool_down=12
        self.ran=800
    def act(self,x,y):
        self.owner.set_v(x,y)
        self.summon(unit.decorator(model.闪光(0.5)))

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

class 咆哮(magic):
    def __init__(self):
        super().__init__()
        self.song_time=0.4
        self.cool_down=10
    def act(self):
        r=150
        self.owner.add_ef(effect.slow(life_time=2.5,percent=1.5))
        self.owner.model.append(model.爆炸(r*2/4,t=0.4,color=(255,180,100)))
        self.owner.model.append(model.爆炸(r*3/4,t=0.3,color=(255,180,100)))
        self.owner.model.append(model.爆炸(r,t=0.2,color=(255,180,100)))


class 闪电(magic):
    def __init__(self):
        super().__init__()
        self.name='「不稳定电流」'
        self.song_time=0.1
        self.cool_down=4
        self.cost=80
    def act(self):
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
        tar_pool=list(filter(lambda i: not i.imm()
                                    and (t.v-i.v).mo()<self.r
                        , unit.unit_pool))
        for i in tar_pool:
            t.add_ef(effect.eat(eat_unit=i))


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


#尽管最后的神风无法保护什么，却最令人怀念。
class 神风(magic):
    def __init__(self):
        super().__init__()
        self.name='玉碎「神风神风神风。」'
        self.song_time=0.2
        self.cost=1
        self.cool_down=1
    def act(self,x,y):
        for i in range(8):
            v=self.owner.v+vec(100,0).adjust_angle(3.14/4*i)
            v2=vec(x,y)+vec(100,0).adjust_angle(3.14/4*i+3.14)
            self.summon(unit.kamikaze(v2-v),x=v.x,y=v.y)



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
        self.ran=800
    def act(self,x,y):
        self.summon(unit.decorator(model.激光(color=(125,125,125),t=0.4,pos=(x,y),r=self.r*2)))
        for i in self.sel_line(self.owner.v,vec(x,y)):
            if i is not self.owner: 
                i.add_ef(effect.forced_move(self.owner.v.x,self.owner.v.y))

class 奥术鹰隼(magic):
    def __init__(self):
        super().__init__()
        self.name='「奥术鹰隼」'
        self.song_time=0.2
        self.cost=70
        self.cool_down=3
        self.power=40
        self.ran=500
    def act(self,target):
        t=self.summon(unit.arrow_to_u(target,act=lambda:self.dam(target,self.power),set_model=model.鸟箭()))
        t.die_model=model.爆炸(45,0.2,color=(155,250,130))
        t.add_ef(effect.bomb(r=25,power=self.power))

class 震荡光弹(magic):
    def __init__(self):
        super().__init__()
        self.name='「震荡光弹」'
        self.song_time=0
        self.cost=90
        self.cool_down=10
    def act(self):
        tar_pool=list(filter(lambda i: i.player!=self.owner.player 
                                and isinstance(i,unit.real_unit)
                    , unit.unit_pool))
        if not tar_pool: return 
        target=min(tar_pool,key = lambda x:(x.v-self.owner.v).mo())
        
        t=self.summon(unit.arrow_to_u(target,set_model=model.圆形(r=10)))
        t.speed=850
        t.die_model=model.爆炸(100,0.2,color=(155,210,130))
        t.add_ef(effect.bomb(aoe=True,r=-1,aoe_r=100,power=50,
            func=lambda x:x.add_ef(effect.slow(2,0.5)) ) )
        
class 上古封印(magic):
    def __init__(self):
        super().__init__()
        self.name='「上古封印」'
        self.song_time=0.2
        self.cost=110
        self.cool_down=15
        self.t=3
    def act(self,target):
        target.add_ef(effect.silence(self.t))
        target.add_ef(effect.amp(self.t,0.5))
        
class 神秘之耀(magic):
    def __init__(self):
        super().__init__()
        self.name='天怒「神秘之耀」'
        self.song_time=0.2
        self.cost=350
        self.cool_down=20
    def act(self,x,y):
        t=self.summon(unit.token(),2.4,x,y)
        t.add_ef(effect.fire(r=100,power=80))
    

        
        
        
        
        
    
if __name__=='__main__':
    pass
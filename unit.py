import pygame
import random
import magic
import model
rd = random.randint
from screen import screen
import ev
from tool import *
import effect

unit_pool=my_list(None)

class unit():
    def __init__(self):
        self.effect=my_list(self)
        self.magic =my_list(self)
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
        self.mana_rc=0         #回魔速度
        self.hp_rc=0          #回血速度
        self.die_model=None     #死亡时播放的模型
        self.now_cmd=('hold',None)
        self.face=vec(0,0)      #朝向
        
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
            v_tar=self.now_cmd[1]
            v=v_tar-self.v
            v.normalize()
            self.face=v
            go=v*t*self.get_speed()
            if go.mo()>(v_tar-self.v).mo():
                self.v=v_tar
            else:
                self.v+=go

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
#写法 cmd('干什么',x,y)
#         cmd(x,y) 默认是移动
#         cmd(vec) 也可以把x,y用向量表示
    def cmd(self,*d):
        # print(x,y)
        ev.ev(self,'_cmd',d)
    def _cmd(self,d):
        if type(d[0])!=str:
            d=('move',*d)
            
        s=d[0]
        if s=='hold':
            self.now_cmd=('hold',None)
        elif s=='move': 
            if type(d[1])==vec:
                self.now_cmd=('move',d[1])
            else:
                self.now_cmd=('move',vec(d[1],d[2]))
        else:
            raise BaseException('无法识别的命令')


#位移
    def set_v(self,x,y):
        ev.ev(self,'_set_v',x,y)
    def _set_v(self,x,y):
        self.v.x=x
        self.v.y=y
        self.cmd('hold')

#召唤另一个单位
    def summon(self,u,t=None,x=None,y=None):
        if u==None : return 
        if not x and not y:
            x=self.v.x
            y=self.v.y
        u.player=self.player
        if t:
            u.add_ef(effect.kill_pass_time(t))
        u.set_v(x,y)
        unit_pool.append(u)
        return u

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
        ev.ev(self,'_cast',magic,x,y)
    def _cast(self,magic,x,y):
        magic.call(x,y)

#单位死亡(事件)
    def die(self):
        ev.ev(self,'_die')
    def _die(self):
        if not self.iki:
            return
        self.iki=False
        for i in self.effect:
            i.die()
        if self.die_model:
            self.summon(decorator(self.die_model))
        
#受到来自源的伤害(事件)
    def hurt(self,source=None,x=100):
        if not source:
            source=self
        ev.ev(self,'_hurt',source,x)
    def _hurt(self,source,x):
        pass
        
#受到来自源的回复(事件)
    def heal(self,source=None,x=100):
        if not source:
            source=self
        ev.ev(self,'_heal',source,x)
    def _heal(self,source,x):
        pass

#对目标造成伤害(事件)
    def dam(self,tar,x):
        ev.ev(self,'_dam',tar,x)
    def _dam(self,tar,x):
        tar.hurt(self,x)

#——————————————————————————————————————————
#——————————————————————————————————————————
#——————————————————————————————————————————
#——————————————————————————————————————————


class real_unit(unit):
    def __init__(self):
        super().__init__()

    def birth(self):
        a=self.player
        if a!=0 :
            color=(a//200//200%200+55,a//200%200+55,a%200+55)
            self.model.reverse()    #作大死
            self.model.append(model.血条(color=color))    
            self.model.append(model.蓝条())    
            self.model.reverse()    
        else:
            self.model.reverse()    #作大死
            self.model.append(model.血条())
            self.model.reverse()

    def _hurt(self,source,x):
        self.hp-=x
        if self.hp<=0:
            self.die()
    def _heal(self,source,x):
        self.hp+=x
        if self.hp>self.maxhp:
            self.hp=self.maxhp

class test_unit(real_unit):
    def __init__(self):
        super().__init__()
        self.model.append(model.圆形())
        self.add_ef(effect.go233())
        self.add_ef(effect.limit_screen())
        self.speed=200
        self.maxhp=100
        self.hp=100
        self.die_model=model.圆形消失(0.6)

class abst_unit(unit):
    def __init__(self):
        super().__init__()
        self.add_ef(effect.magic_imm())

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
        
class arrow(abst_unit):
    def __init__(self):
        super().__init__()
        self.speed=300
        
class arrow_to_u(arrow):
    def __init__(self,tar,act=lambda:0):
        super().__init__()
        self.model.append(model.晕眩())
        self.tar=tar
        self.act=act
    def time_pass(self,time):
        arrow.time_pass(self,time)
        self.cmd(self.tar.v.x,self.tar.v.y)
        if (self.tar.v-self.v).mo()<10:
            self.act()
            self.die()
                    
class arrow_to_d(arrow):
    def __init__(self,x,y,set_model=model.箭头()):
        super().__init__()
        self.speed=400
        self.model.append(set_model)
        self.add_ef(effect.kill_out_screen())
        self.p_v=vec(x,y)
        self.die_model=model.爆炸(80,0.2)

    def time_pass(self,time):
        arrow.time_pass(self,time)
        self.cmd(self.v+self.p_v)


class ship(real_unit):
    def __init__(self):
        super().__init__()
        self.speed=110
        self.maxhp=250
        self.hp=250
        self.model.append(model.方块(r=24))
        self.add_ef(effect.funnel())
        self.add_ef(effect.go233(r=1000,expect=2))
        self.add_ef(effect.limit_screen())
        self.die_model=model.爆炸(r=70,t=0.4)        
        

class hero(real_unit):
    def __init__(self):
        super().__init__()
        self.set_v(rd(0,1366),rd(0,768))
        self.speed=220
        self.maxhp=300
        self.hp=300
        self.mana_rc=25
        self.hp_rc=2
        self.add_ef(effect.dam_imm(t=2))
        
        
class bird(hero):
    def __init__(self):
        super().__init__()
        self.add_ef(effect.limit_screen())
        # self.add_ef(effect.silence())
        
        self.magic.append(magic.射箭())
        self.magic.append(magic.大量射箭())
        self.magic.append(magic.气球炸弹())
        self.magic.append(magic.若风一指())
        
        self.model.append(model.头像(name='bird'))
        
        # self.add_ef()
        # self.add_ef(effect.slience())
        
class rimo(hero):
    def __init__(self):
        super().__init__()
        
        # self.add_ef(effect.fire(r=100,power=10))
        # self.add_ef(effect.one_dam(r=100))
        # self.add_ef(effect.vampire())
        # self.add_ef(effect.silence())
        
        self.magic.append(magic.召唤舰队())
        self.magic.append(magic.闪电())
        self.magic.append(magic.闪现())
        self.magic.append(magic.绿色原谅光线())
        
        self.model.append(model.头像(name='rimo'))

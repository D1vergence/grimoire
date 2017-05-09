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
            if go.mo()<(v_tar-self.v).mo():
                self.v+=go
            else:
                self.v=v_tar
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
            t=decorator(self.die_model)
            t.set_v(self.v)
            unit_pool.append(t)
        
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

    def birth(self):
        a=self.player
        if a!=0 :
            color=(a//200//200%200+55,a//200%200+55,a%200+55)
            self.model.append(model.血条(color=color))    
            self.model.append(model.蓝条())    
        else:
            self.model.append(model.血条())

    def _hurt(self,damage):
        self.hp-=damage.value
        if self.hp<=0:
            self.die()
    def _heal(self,x):
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
        self.maxhp=60
        self.hp=60
        self.die_model=model.圆形消失(0.6)
        
        # self.add_ef(effect.funnel())
        # self.add_ef(effect.bomb(r=4,power=70,aoe=True,aoe_r=100))
        # self.add_ef(effect.closing())
        # self.die_model=model.爆炸(t=0.3,r=100)
        # self.player=random.random()

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
        
class arrow(token):
    def __init__(self):
        super().__init__()
        self.speed=300

#指向单位的箭矢
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

        self.model.append(model.头像(name=self.__class__.__name__))
        
        
class bird(hero):
    def __init__(self):
        super().__init__()
        self.speed=235
        self.add_ef(effect.limit_screen())
        # self.add_ef(effect.silence())
        
        self.magic.append(magic.光之矢())
        self.magic.append(magic.虚伪的磐舟())
        self.magic.append(magic.冰之矢())
        self.magic.append(magic.若风一指())
        
        
class suin(hero):
    def __init__(self):
        super().__init__()
        
        # self.add_ef(effect.fire(r=100,power=10))
        # self.add_ef(effect.one_dam(r=100))
        # self.add_ef(effect.vampire())
        # self.add_ef(effect.silence())
        
        self.magic.append(magic.原谅光线())
        self.magic.append(magic.星河漩涡())
        self.magic.append(magic.闪现())
        self.magic.append(magic.舰队())
        
        
class rimo(hero):
    def __init__(self):
        super().__init__()
        self.magic.append(magic.烈焰风暴())
        self.magic.append(magic.沉默风暴())
        self.magic.append(magic.闪电())
        self.magic.append(magic.ghost_parade())
        
class pandaye(hero):
    def __init__(self):
        super().__init__()
        self.magic.append(magic.轨道坠落())
        self.magic.append(magic.断电导弹())
        self.magic.append(magic.气球炸弹())
        self.magic.append(magic.panux连线())
        
        

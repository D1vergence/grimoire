import random
rd=random.randint

import unit
import effect
import hero

size=(4000,4000)

def time_pass(time_passed):
    None
    # if random.random()<time_passed/2.3:
        # if len(unit.unit_pool)<10:
            # t=unit.sheep()
            # t.set_v(rd(0,1366),rd(0,768))
            # unit.unit_pool.append(t)

#让英雄在死亡的时候复活
def hero_die():
    t=hero.hero.die
    def f(self,damage):
        t(self,damage)
        if self.player==1:
            self.set_v(100,size[1]-100)
        if self.player==2:
            self.set_v(size[0]-100,100)
        self.iki=True
        self.hp=self.maxhp
        self.mana=self.max_mana
    return f
hero.hero.die=hero_die()

#设置英雄出生点
def hero_init():
    t=hero.hero.birth
    def f(self):
        t(self)
        if self.player==1:
            self.set_v(100,size[1]-100)
        if self.player==2:
            self.set_v(size[0]-100,100)
    return f
hero.hero.birth=hero_init()


#放置双方防御塔和出兵点

def create(player,u,x,y):
    u.set_v(x,y)
    u.player=player
    unit.unit_pool.append(u)
    return u
    
create(1,unit.tower(),480,size[1]-400)
create(1,unit.tower(),1080,size[1]-1000)
create(1,unit.tower(),1680,size[1]-1600)
create(1,unit.token(),100,size[1]-100).add_ef(effect.unit_gen(unit=unit.soldier,cd=20,mult=4))

create(2,unit.tower(),size[0]-480,400)
create(2,unit.tower(),size[0]-1080,1000)
create(2,unit.tower(),size[0]-1680,1600)
create(2,unit.token(),size[0]-100,100).add_ef(effect.unit_gen(unit=unit.soldier,cd=20,mult=4))



#放置石头
def s(r,x,y):
    t=unit.stone(r)
    t.set_v(x,y)
    unit.unit_pool.append(t)

def s2(r,x,y):
    s(r,x,y)
    s(r,size[0]-x,size[1]-y)

def s4(r,x,y):
    s2(r,x,y)
    s2(r,y,x)
#边界的石头
s2(300,0,0)
s4(200,450,0)
s4(100,700,0)
s4(140,920,0)
s4(200,1160,0)
s4(220,1560,0)
s4(140,1860,0)
s4(100,2060,0)

    

#路上的石头
x,y=(1450,1950)
for i in range(15):
    s2(80,x,size[1]-y)
    s2(80,y,size[1]-x)
    x-=80
    y-=80
    
    
x,y=(1550,2050)
for i in range(8):
    s2(80,x,size[1]-y)
    s2(80,y,size[1]-x)
    x-=80
    y+=80




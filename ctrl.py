import effect
import unit
import hero

import random
rd = random.randint

class player():
    def __init__(self):
        self.me=None
        
    @property
    def info(self):
        info=['233',[],[0,0],[0,0],1]
        if not self.me:
            return info
        for i in self.me.magic:
            try:
                name=i.name
            except:
                name=i.__class__.__name__
            info[1].append(('[%s] %s'%(i.key.upper(),name) , i.cool_down_left))
        info[2]=[self.me.hp, self.me.maxhp]
        info[3]=[self.me.mana, self.me.max_mana]
        info[4]=self.me.exp
        return info
    
    def set_hero(self,n):
        try:
            self.me.die()
        except:
            None
        if n==1:
            self.me=hero.bird()
        if n==2:
            self.me=hero.suin()
        if n==3:
            self.me=hero.rimo()
        if n==4:
            self.me=hero.pandaye()
        # self.me.player=hash(self)
        self.me.player=rd(1,2)  #23333
        unit.unit_pool.append(self.me)
        self.ctrler=ctrler(self.me)

class ctrler():
    def __init__(self,me):
        self.me=me
    def mov(self,x,y):
        self.me.cmd(x,y)
    def magic(self,l,x,y):
        mg=self.me.magic.find(l)
        if mg:
            self.me.cast(mg, x, y)
    def hold(self):
        self.me.cmd('hold')
    
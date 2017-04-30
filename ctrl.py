import effect
import unit
import random

rd = random.randint

class player():
    def __init__(self):
        self.me=None
        
    @property
    def info(self):
        info=['233',[],[0,0],[0,0]]
        if not self.me:
            return info
        for i in self.me.magic:
            try:
                name=i.name
            except:
                name=i.__class__.__name__
            info[1].append((name,i.cool_down_left))
        info[2]=[self.me.hp, self.me.maxhp]
        info[3]=[self.me.mana, self.me.max_mana]
        return info
    
    def set_hero(self,n):
        try:
            self.me.die()
        except:
            None
        if n==1:
            self.me=unit.bird()
        if n==2:
            self.me=unit.rimo()
        self.me.player=hash(self)
        unit.unit_pool.append(self.me)
        self.ctrler=ctrler(self.me)

class ctrler():
    def __init__(self,me):
        self.me=me
    def mov(self,x,y):
        self.me.cmd(x,y)
    def magic(self,l,x,y):
        self.me.cast(self.me.magic[l], x, y)
    def hold(self):
        self.me.cmd('hold')
    
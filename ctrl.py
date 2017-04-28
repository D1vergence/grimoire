import effect
import unit
import random

rd = random.randint

class player():
    def __init__(self):
        self.me=None
        
    @property
    def info(self):
        info=('233',[])
        if not self.me: 
            return info
        for i in self.me.magic:
            info[1].append(i.cool_down_left)
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
    
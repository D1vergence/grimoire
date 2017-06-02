import effect,unit,damage
from tool import *

#这是法术和效果的基类
#定义了一些普遍需要用到的操作

class fantasy():
#造成伤害
    def dam(self,tar,x,kind='magic'):   #kind='physic'
        dam=damage.damage(x,kind,self)
        self.owner.dam(tar,dam)
        
#召唤另一个单位
    def summon(self,u,t=None,x=None,y=None):
        if u==None : return 
        if not x and not y:
            x=self.owner.v.x
            y=self.owner.v.y
        u.player=self.owner.player
        if t:
            u.add_ef(effect.kill_pass_time(t))
        u.set_v(x,y)
        if isinstance(u,unit.token):
            u.add_ef(effect.agent(master=self.owner))
        unit.unit_pool.append(u)
        return u
        
#圆形选择器
    def sel(self,r,x=None,y=None):
        pass
        
#线选择器
    def sel_line(self,v,v2):
        if v==v2:
            v2.x+=1
        sel_line=[]
        x1,y1=(v.x,v.y) 
        x2,y2=(v2.x,v2.y)
        
        a=y2-y1
        b=x1-x2
        c=(y1-y2)*x1+(x2-x1)*y1
        for i in unit.unit_pool:
            d=abs(a*i.v.x+b*i.v.y+c)/(a*a+b*b)**0.5
            if d<self.r and vec(x2-x1,y2-y1)*(i.v-v)>0:
                sel_line.append(i)
        return sel_line
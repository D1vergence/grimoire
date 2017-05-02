import effect,unit,damage

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
        unit.unit_pool.append(u)
        return u
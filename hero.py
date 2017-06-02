import model
import magic
import effect
import unit

import random
rd = random.randint

class hero(unit.real_unit):
    def __init__(self):
        super().__init__()
        self.speed=220
        self.maxhp=400
        self.hp=400
        self.mana_rc=10
        self.hp_rc=2
        self.add_ef(effect.dam_imm(t=3.3))
        self.magic.append(magic.攻击())
        self.size=20

        self.model.append(model.头像(name=self.__class__.__name__))
    def die(self,damage):
        unit.real_unit.die(self,damage)
        
        
class bird(hero):
    def __init__(self):
        super().__init__()
        self.speed=240
        
        self.magic.append(magic.奥术鹰隼())
        self.magic.append(magic.震荡光弹())
        self.magic.append(magic.上古封印())
        self.magic.append(magic.神秘之耀())
        
        
class suin(hero):
    def __init__(self):
        super().__init__()
        
        self.magic.append(magic.原谅光线())
        self.magic.append(magic.星河漩涡())
        self.magic.append(magic.闪现())
        self.magic.append(magic.舰队())
        
        
class rimo(hero):
    def __init__(self):
        super().__init__()
        self.magic.append(magic.烈焰风暴())
        self.magic.append(magic.纸上城壁())
        self.magic.append(magic.死者的叹息())
        self.magic.append(magic.ghost_parade())
        
class pandaye(hero):
    def __init__(self):
        super().__init__()
        self.magic.append(magic.轨道坠落())
        self.magic.append(magic.断电导弹())
        self.magic.append(magic.神风())
        self.magic.append(magic.panux连线())
        
        
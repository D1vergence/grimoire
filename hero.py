import model
import magic
import effect
import unit

import random
rd = random.randint

class hero(unit.real_unit):
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
        
        self.magic.append(magic.光之矢())
        self.magic.append(magic.虚伪的磐舟())
        self.magic.append(magic.冰之矢())
        self.magic.append(magic.若风一指())
        
        
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
        self.magic.append(magic.沉默风暴())
        self.magic.append(magic.闪电())
        self.magic.append(magic.ghost_parade())
        
class pandaye(hero):
    def __init__(self):
        super().__init__()
        self.magic.append(magic.轨道坠落())
        self.magic.append(magic.断电导弹())
        self.magic.append(magic.神风())
        self.magic.append(magic.panux连线())
        
        
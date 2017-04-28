class ev():
    def __init__(self,unit,kind,*arg):
        self.unit=unit
        self.kind=kind
        self.arg=list(arg)
        for i in unit.effect:   #注意！这里的self改变了！23333
            self=i.change(self)
            if self==None:
                return
        self.go()
    def go(self):
        eval('self.unit.%s(*self.arg)' % self.kind)
        if self.arg:
            self.rep=self.arg[-1]
        else:
            return None
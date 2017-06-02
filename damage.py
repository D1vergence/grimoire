import effect
class damage():
    def __init__(self,value,kind,source):
        self.value=value
        self.kind=kind
        self._source=source
        
    @property
    def source_unit(self):
        while True:
            t=self._source.owner
            for i in t.effect:
                if isinstance(i,effect.agent):
                    t=i.master
                    continue
            break
        # print(t)
        # print(t.effect)
        return t
        
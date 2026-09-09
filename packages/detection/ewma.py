from dataclasses import dataclass
@dataclass(slots=True)
class EWMA:
    alpha:float=0.3
    value:float|None=None
    def __post_init__(self)->None:
        if not 0 < self.alpha <= 1: raise ValueError('alpha must be in (0,1]')
    def update(self,x:float,*,learn:bool=True)->float:
        if self.value is None: self.value=x
        elif learn: self.value=self.alpha*x+(1-self.alpha)*self.value
        return self.value

from dataclasses import dataclass
@dataclass(slots=True)
class CUSUM:
    target:float; drift:float=0.5; threshold:float=5.0; positive:float=0.0; negative:float=0.0
    def update(self,x:float)->bool:
        self.positive=max(0.0,self.positive+x-self.target-self.drift)
        self.negative=min(0.0,self.negative+x-self.target+self.drift)
        return self.positive>self.threshold or abs(self.negative)>self.threshold

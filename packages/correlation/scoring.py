from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class CorrelationContext:
    seconds_apart:float
    topology_distance:int|None
    shared_trace:bool
    same_deployment:bool
    semantic_similarity:float

def correlation_score(c:CorrelationContext)->float:
    temporal=max(0.0,1.0-min(c.seconds_apart,300.0)/300.0)
    topology=0.0 if c.topology_distance is None else 1.0/(1+c.topology_distance)
    trace=1.0 if c.shared_trace else 0.0
    deploy=1.0 if c.same_deployment else 0.0
    semantic=max(0.0,min(c.semantic_similarity,1.0))
    return round(0.30*temporal+0.20*topology+0.20*trace+0.20*deploy+0.10*semantic,6)

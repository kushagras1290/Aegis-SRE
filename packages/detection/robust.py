from dataclasses import dataclass
from math import isfinite
from statistics import median

@dataclass(frozen=True,slots=True)
class AnomalyResult:
    score:float; observed:float; expected:float; anomalous:bool

def robust_zscore(values:list[float],observed:float,threshold:float=3.5)->AnomalyResult:
    if len(values)<3: raise ValueError('at least 3 baseline values required')
    med=median(values); mad=median([abs(x-med) for x in values])
    if mad==0:
        score=0.0 if observed==med else (threshold+1.0)
    else:
        score=0.6745*(observed-med)/mad
    if not isfinite(score): score=threshold+1.0
    return AnomalyResult(score=score,observed=observed,expected=med,anomalous=abs(score)>=threshold)

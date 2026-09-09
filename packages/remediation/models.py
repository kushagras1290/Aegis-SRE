from enum import StrEnum
from pydantic import BaseModel,Field
class Risk(StrEnum): LOW='low'; MEDIUM='medium'; HIGH='high'
class ActionName(StrEnum): RESTART_POD='restart_pod'; ROLLBACK_DEPLOYMENT='rollback_deployment'; SCALE_DEPLOYMENT='scale_deployment'; PAUSE_ROLLOUT='pause_rollout'; RESUME_ROLLOUT='resume_rollout'; DISABLE_FEATURE_FLAG='disable_feature_flag'; INVALIDATE_CACHE='invalidate_cache'; REROUTE_TRAFFIC='reroute_traffic'
class RemediationAction(BaseModel):
    action:ActionName
    service:str=Field(min_length=1,max_length=128)
    environment:str=Field(min_length=1,max_length=64)
    parameters:dict[str,str|int|float|bool]=Field(default_factory=dict)
    risk:Risk=Risk.MEDIUM
class Approval(BaseModel): actor:str; approved:bool

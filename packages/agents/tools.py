from dataclasses import dataclass
READ_ONLY_TOOLS=frozenset({'query_logs','query_metrics','get_trace','get_service_topology','get_deployments','get_kubernetes_events','get_pods','describe_deployment','get_previous_incidents','search_runbooks','search_postmortems'})
@dataclass(frozen=True,slots=True)
class QueryLogsRequest:
    organization_id:str; service:str; environment:str; start_epoch:int; end_epoch:int; limit:int=100
    def __post_init__(self)->None:
        if self.end_epoch<=self.start_epoch: raise ValueError('invalid time range')
        if self.limit<1 or self.limit>1000: raise ValueError('limit must be 1..1000')

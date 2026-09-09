from typing import Any
_REQUIRED=('timestamp','tenant_id','environment','service.name')
def normalize(record:dict[str,Any])->dict[str,Any]:
    out=dict(record)
    if 'organization_id' in out and 'tenant_id' not in out: out['tenant_id']=out['organization_id']
    missing=[k for k in _REQUIRED if k not in out]
    if missing: raise ValueError('missing canonical telemetry fields: '+','.join(missing))
    return out

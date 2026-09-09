import pytest
from packages.telemetry.normalize import normalize
def test_aliases_org_to_tenant():
 x=normalize({'timestamp':1,'organization_id':'o','environment':'p','service.name':'api'}); assert x['tenant_id']=='o'
def test_missing_rejected():
 with pytest.raises(ValueError): normalize({'timestamp':1})

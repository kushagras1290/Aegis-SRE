import pytest
from packages.agents.model_gateway import ModelGateway
from packages.agents.tools import QueryLogsRequest,READ_ONLY_TOOLS
class Bad:
 def complete(self,prompt): raise TimeoutError
class Good:
 def __init__(self): self.prompt=''
 def complete(self,prompt): self.prompt=prompt; return 'ok'
def test_failover_and_redaction():
 g=Good(); assert ModelGateway([Bad(),g]).complete('Authorization: Bearer abcdef123')=='ok'; assert 'abcdef123' not in g.prompt
def test_all_fail():
 with pytest.raises(RuntimeError): ModelGateway([Bad()]).complete('x')
def test_no_mutation_tools(): assert 'rollback_deployment' not in READ_ONLY_TOOLS
def test_query_bounds():
 with pytest.raises(ValueError): QueryLogsRequest('o','s','p',10,20,1001)

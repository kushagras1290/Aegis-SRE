import networkx as nx
import pytest
from packages.rca.graph import rank_causes
def graph():
 g=nx.DiGraph(); g.add_edges_from([('db','checkout'),('checkout','gateway'),('redis','checkout')]); return g
def test_db_can_rank_first(): assert rank_causes(graph(),'gateway',{'db':1,'checkout':.4},{'db':.8})[0].resource=='db'
def test_missing_affected():
 with pytest.raises(ValueError): rank_causes(graph(),'missing',{})
def test_sorted_desc():
 r=rank_causes(graph(),'gateway',{'db':1,'checkout':.4}); assert [x.score for x in r]==sorted([x.score for x in r],reverse=True)

from dataclasses import dataclass
import networkx as nx
@dataclass(frozen=True,slots=True)
class Candidate:
    resource:str; score:float

def rank_causes(graph:nx.DiGraph,affected:str,anomaly:dict[str,float],change:dict[str,float]|None=None)->list[Candidate]:
    change=change or {}
    if affected not in graph: raise ValueError('affected node missing from topology')
    pr=nx.pagerank(graph) if graph.number_of_nodes() else {}
    out=[]
    for node in graph.nodes:
        try: dist=nx.shortest_path_length(graph,node,affected); proximity=1/(1+dist)
        except nx.NetworkXNoPath: proximity=0.0
        score=0.55*anomaly.get(node,0.0)+0.25*proximity+0.15*change.get(node,0.0)+0.05*pr.get(node,0.0)
        out.append(Candidate(str(node),round(score,6)))
    return sorted(out,key=lambda x:x.score,reverse=True)

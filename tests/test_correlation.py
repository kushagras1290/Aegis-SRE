from packages.correlation.scoring import CorrelationContext,correlation_score
def test_related_scores_high(): assert correlation_score(CorrelationContext(5,1,True,True,.9))>.75
def test_unrelated_scores_low(): assert correlation_score(CorrelationContext(1000,None,False,False,0))==0
def test_semantic_clamped(): assert correlation_score(CorrelationContext(1000,None,False,False,99))==.1

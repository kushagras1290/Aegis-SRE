import pytest
from packages.detection.robust import robust_zscore
from packages.detection.ewma import EWMA
from packages.detection.cusum import CUSUM
def test_robust_anomaly(): assert robust_zscore([1,1.1,.9,1.0,1.05],4).anomalous
def test_zero_mad_is_finite(): assert robust_zscore([1,1,1],2).score<100
def test_small_baseline_rejected():
 with pytest.raises(ValueError): robust_zscore([1,2],3)
def test_ewma():
 e=EWMA(.5); assert e.update(10)==10; assert e.update(14)==12
def test_ewma_freeze():
 e=EWMA(.5); e.update(10); assert e.update(100,learn=False)==10
def test_bad_alpha():
 with pytest.raises(ValueError): EWMA(0)
def test_cusum_shift():
 c=CUSUM(target=0,drift=.1,threshold=1); assert any(c.update(1) for _ in range(3))

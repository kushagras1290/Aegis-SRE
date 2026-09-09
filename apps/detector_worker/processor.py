from __future__ import annotations

from dataclasses import dataclass

from packages.detection.robust import AnomalyResult, robust_zscore


@dataclass(frozen=True, slots=True)
class MetricSample:
    signal: str
    observed: float
    baseline: list[float]


def process_metric(sample: MetricSample) -> AnomalyResult:
    return robust_zscore(sample.baseline, sample.observed)

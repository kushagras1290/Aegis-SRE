from packages.correlation.scoring import CorrelationContext, correlation_score


def process_correlation(context: CorrelationContext) -> float:
    return correlation_score(context)

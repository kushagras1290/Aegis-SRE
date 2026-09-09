from packages.observability.context import TraceContext, get_trace_context, set_trace_context


def test_context_round_trip() -> None:
    expected = TraceContext(
        request_id="req-1",
        trace_id="trace-1",
        incident_id="inc-1",
        organization_id="org",
    )
    set_trace_context(expected)
    assert get_trace_context() == expected

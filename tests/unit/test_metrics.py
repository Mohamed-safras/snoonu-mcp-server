import pytest

from src.metrics import TOOL_CALL_COUNT, instrument_tool


def test_instrument_tool_counts_success_and_returns_result():
    @instrument_tool("unit_test_tool_success")
    def fn(x):
        return x + 1

    before = TOOL_CALL_COUNT.labels("unit_test_tool_success", "success")._value.get()
    assert fn(1) == 2
    assert TOOL_CALL_COUNT.labels("unit_test_tool_success", "success")._value.get() == before + 1


def test_instrument_tool_counts_error_and_reraises():
    @instrument_tool("unit_test_tool_error")
    def fn():
        raise ValueError("boom")

    before = TOOL_CALL_COUNT.labels("unit_test_tool_error", "error")._value.get()
    with pytest.raises(ValueError, match="boom"):
        fn()
    assert TOOL_CALL_COUNT.labels("unit_test_tool_error", "error")._value.get() == before + 1

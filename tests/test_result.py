from result import Result


def test_ok_result_splits_stdout_into_lines():
    result = Result(stdout="a\nb\nc")

    assert result.ok is True
    assert result.error is None
    assert result.lines == ["a", "b", "c"]


def test_ok_result_with_empty_stdout_has_no_lines():
    result = Result(stdout="")

    assert result.lines == []


def test_error_result_has_no_lines():
    result = Result(stdout=None, ok=False, error="boom")

    assert result.ok is False
    assert result.error == "boom"
    assert result.lines == []


def test_repr_reflects_ok_state():
    assert "ok=True" in repr(Result(stdout="x"))
    assert "ok=False" in repr(Result(stdout=None, ok=False, error="boom"))

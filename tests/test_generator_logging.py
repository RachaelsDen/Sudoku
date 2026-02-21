import logging

import pytest

from src.base.generator_base import GeneratorBase


class _FakeQueue:
    def __init__(self):
        self._items = []

    def put(self, item):
        self._items.append(item)

    def get(self):
        return self._items.pop(0)

    def empty(self):
        return len(self._items) == 0


class _TestGenerator(GeneratorBase):
    def _generate_impl(self, difficulty: float):
        return [[1]], [[1]]


def test_success_logs_start_and_success(monkeypatch, caplog):
    import src.base.generator_base as genmod

    t = iter([10.0, 10.125])
    monkeypatch.setattr(genmod.time, "time", lambda: next(t))
    monkeypatch.setattr(genmod.mp, "Queue", lambda: _FakeQueue())

    class _FakeProcess:
        def __init__(self, target, args):
            self._target = target
            self._args = args
            self._alive = False
            self.exitcode = None

        def start(self):
            self._alive = True
            self._target(*self._args)
            self.exitcode = 0
            self._alive = False

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return self._alive

        def terminate(self):
            self.exitcode = -15
            self._alive = False

    monkeypatch.setattr(genmod.mp, "Process", _FakeProcess)

    gen = _TestGenerator()
    with caplog.at_level(logging.INFO, logger="src.base.generator_base"):
        puzzle, solution = gen.generate(0.7, timeout=5)

    assert puzzle == [[1]]
    assert solution == [[1]]

    records = [r for r in caplog.records if r.name == "src.base.generator_base"]
    messages = [r.getMessage() for r in records]

    assert any(
        "Starting puzzle generation" in m and "difficulty=0.7" in m and "timeout=5" in m
        for m in messages
    )
    assert any(
        "Puzzle generated successfully" in m and "duration_ms=125" in m for m in messages
    )


def test_timeout_logs_warn_with_difficulty_and_timeout(monkeypatch, caplog):
    import src.base.generator_base as genmod

    monkeypatch.setattr(genmod.mp, "Queue", lambda: _FakeQueue())

    class _FakeProcess:
        def __init__(self, target, args):
            self._alive = True
            self.exitcode = None

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return self._alive

        def terminate(self):
            self.exitcode = -15
            self._alive = False

    monkeypatch.setattr(genmod.mp, "Process", _FakeProcess)

    gen = _TestGenerator()
    with caplog.at_level(logging.INFO, logger="src.base.generator_base"):
        with pytest.raises(TimeoutError):
            gen.generate(0.2, timeout=3)

    warn_records = [
        r
        for r in caplog.records
        if r.name == "src.base.generator_base" and r.levelno == logging.WARNING
    ]
    assert len(warn_records) == 1
    msg = warn_records[0].getMessage()
    assert "Puzzle generation timed out" in msg
    assert "difficulty=0.2" in msg
    assert "timeout=3" in msg


def test_failure_logs_error_with_exitcode_and_is_alive(monkeypatch, caplog):
    import src.base.generator_base as genmod

    monkeypatch.setattr(genmod.mp, "Queue", lambda: _FakeQueue())

    class _FakeProcess:
        def __init__(self, target, args):
            self._alive = False
            self.exitcode = 7

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return self._alive

        def terminate(self):
            self.exitcode = -15
            self._alive = False

    monkeypatch.setattr(genmod.mp, "Process", _FakeProcess)

    gen = _TestGenerator()
    with caplog.at_level(logging.INFO, logger="src.base.generator_base"):
        with pytest.raises(RuntimeError):
            gen.generate(0.9, timeout=5)

    error_records = [
        r
        for r in caplog.records
        if r.name == "src.base.generator_base" and r.levelno == logging.ERROR
    ]
    assert len(error_records) == 1
    msg = error_records[0].getMessage()
    assert "Puzzle generation failed" in msg
    assert "exitcode=7" in msg
    assert "is_alive=False" in msg

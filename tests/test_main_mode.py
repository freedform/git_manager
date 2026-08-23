import sys

import pytest
import questionary

import main as main_module
from tests.conftest import FakeQuestion


def test_main_requires_action_when_mode_is_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "cli"])

    with pytest.raises(SystemExit) as exc_info:
        main_module.main()

    assert exc_info.value.code == 1
    assert "--action is required" in capsys.readouterr().out


def test_main_dispatches_to_cli_mode_when_explicit(monkeypatch, git_repo):
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "cli", "-a", "status", "-d", str(git_repo)])

    with pytest.raises(SystemExit) as exc_info:
        main_module.main()

    assert exc_info.value.code == 0


def test_main_ignores_action_and_stays_interactive_without_explicit_mode(monkeypatch):
    """-a/--action alone must not switch into CLI mode -- --mode cli is required."""
    monkeypatch.setattr(sys, "argv", ["main.py", "-a", "status", "-d", "/tmp/whatever"])
    monkeypatch.setattr(questionary, "select", lambda *a, **k: FakeQuestion("exit"))

    main_module.main()  # reaches the interactive loop and exits via "exit", no SystemExit raised

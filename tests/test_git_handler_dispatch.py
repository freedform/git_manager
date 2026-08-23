import pytest

from git_handler import GitMenu


def test_get_actions_lists_git_prefixed_methods_plus_back():
    menu = GitMenu(repo_dir_path="/tmp/whatever")

    actions = menu.get_actions()

    assert "status" in actions
    assert "commit" in actions
    assert actions[-1] == "<< back"


def test_dispatch_routes_to_the_matching_git_method(monkeypatch):
    menu = GitMenu(repo_dir_path="/tmp/whatever")
    called = {}
    monkeypatch.setattr(menu, "_git_status", lambda: called.setdefault("ran", True))

    menu.dispatch("status")

    assert called.get("ran") is True


def test_dispatch_unknown_action_raises_value_error():
    menu = GitMenu(repo_dir_path="/tmp/whatever")

    with pytest.raises(ValueError):
        menu.dispatch("not_a_real_action")

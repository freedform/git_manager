import questionary

from git_handler import GitMenu
from tests.conftest import FakeQuestion


def test_git_status_lists_changed_files(git_repo):
    (git_repo / "new.txt").write_text("new\n")
    menu = GitMenu(repo_dir_path=str(git_repo))

    files = menu._git_status()

    assert files == ["new.txt"]


def test_git_commit_uses_message_from_prompt(monkeypatch, git_repo):
    (git_repo / "new.txt").write_text("new\n")
    menu = GitMenu(repo_dir_path=str(git_repo))
    menu.git.add()
    monkeypatch.setattr(questionary, "text", lambda *a, **k: FakeQuestion("my commit message"))

    menu._git_commit()

    assert "my commit message" in menu.git.log().stdout


def test_git_commit_falls_back_to_auto_commit_when_blank(monkeypatch, git_repo):
    (git_repo / "new.txt").write_text("new\n")
    menu = GitMenu(repo_dir_path=str(git_repo))
    menu.git.add()
    monkeypatch.setattr(questionary, "text", lambda *a, **k: FakeQuestion(""))

    menu._git_commit()

    assert "Auto commit" in menu.git.log().stdout


def test_dispatch_drives_branch_create_end_to_end(monkeypatch, git_repo):
    """dispatch() -> _git_branch -> submenu select -> _sub_branch_create prompt -> real git."""
    menu = GitMenu(repo_dir_path=str(git_repo))
    select_answers = iter(["create", "<< back"])
    monkeypatch.setattr(questionary, "select", lambda *a, **k: FakeQuestion(next(select_answers)))
    monkeypatch.setattr(questionary, "text", lambda *a, **k: FakeQuestion("feature-x"))

    menu.dispatch("branch")

    assert "feature-x" in menu.git.branch_local().lines

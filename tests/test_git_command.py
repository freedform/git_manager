import subprocess
from unittest.mock import patch

from git_command import GitCommand

# --- real-repo integration tests -------------------------------------------

def test_status_on_clean_repo(git_repo):
    git = GitCommand(str(git_repo))

    result = git.status()

    assert result.ok
    assert result.lines == []


def test_status_reports_untracked_file(git_repo):
    (git_repo / "new.txt").write_text("new\n")
    git = GitCommand(str(git_repo))

    result = git.status()

    assert result.ok
    assert result.lines == ["?? new.txt"]


def test_current_branch(git_repo):
    git = GitCommand(str(git_repo))

    result = git.current_branch()

    assert result.ok
    assert result.stdout.strip() == "main"


def test_branch_create_and_list(git_repo):
    git = GitCommand(str(git_repo))

    assert git.branch_create("feature").ok
    branches = git.branch_local()

    assert branches.ok
    assert set(branches.lines) == {"main", "feature"}


def test_add_and_commit(git_repo):
    git = GitCommand(str(git_repo))
    (git_repo / "new.txt").write_text("new\n")

    assert git.add().ok
    result = git.commit(message="add new.txt")

    assert result.ok
    assert git.status().lines == []


def test_commit_with_nothing_staged_fails(git_repo):
    """git writes "nothing to commit" to stdout, not stderr, for this failure.
    __run_command falls back to stdout when stderr is empty (see CLAUDE.md)."""
    git = GitCommand(str(git_repo))

    result = git.commit(message="empty commit")

    assert result.ok is False
    assert "nothing to commit" in result.error


def test_init_creates_repo(tmp_path):
    target = tmp_path / "new_repo"

    result = GitCommand.init(str(target))

    assert result.ok
    assert (target / ".git").is_dir()


# --- mocked-subprocess unit tests for the error paths -----------------------

def test_timeout_is_reported_as_error():
    git = GitCommand("/nonexistent")
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=20)):
        result = git.status()

    assert result.ok is False
    assert "timed out" in result.error.lower()


def test_called_process_error_is_reported():
    git = GitCommand("/nonexistent")
    err = subprocess.CalledProcessError(returncode=128, cmd="git", stderr="fatal: not a git repository\n")
    with patch("subprocess.run", side_effect=err):
        result = git.status()

    assert result.ok is False
    assert result.error == "fatal: not a git repository"


def test_called_process_error_falls_back_to_stdout_when_stderr_empty():
    git = GitCommand("/nonexistent")
    err = subprocess.CalledProcessError(
        returncode=1, cmd="git", stderr="", output="nothing to commit, working tree clean\n"
    )
    with patch("subprocess.run", side_effect=err):
        result = git.status()

    assert result.ok is False
    assert result.error == "nothing to commit, working tree clean"


def test_missing_git_binary_is_reported_as_error_not_raised():
    """subprocess.run raises FileNotFoundError if 'git' isn't on PATH -- this
    must come back as a Result, not an unhandled exception."""
    git = GitCommand("/nonexistent")
    with patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory", "git")):
        result = git.status()

    assert result.ok is False
    assert "git executable not found" in result.error


def test_init_reports_missing_git_binary_too(tmp_path):
    with patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory", "git")):
        result = GitCommand.init(str(tmp_path / "new_repo"))

    assert result.ok is False
    assert "git executable not found" in result.error

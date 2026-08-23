import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    """A real, throwaway git repo on branch 'main' with one commit."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(repo_path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo_path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo_path), "config", "user.name", "Test"], check=True)
    (repo_path / "file.txt").write_text("hello\n")
    subprocess.run(["git", "-C", str(repo_path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo_path), "commit", "-m", "initial commit"], check=True, capture_output=True)
    return repo_path


class FakeQuestion:
    """Stand-in for a questionary Question: .ask() returns a canned answer."""

    def __init__(self, answer):
        self.answer = answer

    def ask(self):
        return self.answer

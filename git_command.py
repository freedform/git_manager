import subprocess
from result import Result


class GitCommand:

    def __init__(self, repo_path: str) -> None:
        self.repo_path = repo_path

    def __run_command(self, command: list) -> Result:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=20,
                check=True
            )
            return Result(
                stdout=result.stdout
            )

        except subprocess.TimeoutExpired as e:
            return Result(
                stdout=None,
                ok=False,
                error=str(e),
            )

        except subprocess.CalledProcessError as e:
            return Result(
                stdout=None,
                ok=False,
                error=(e.stderr or e.stdout or "").strip()
            )

        except FileNotFoundError as e:
            return Result(
                stdout=None,
                ok=False,
                error=f"git executable not found: {e}",
            )

    def status(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "status", "--porcelain"]
        )

    def current_branch(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "rev-parse", "--abbrev-ref", "HEAD"]
        )

    def branch_create(self, branch_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "branch", branch_name]
        )

    def branch_delete(self, branch_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "branch", "-d", branch_name]
        )

    def branch_select(self, branch_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "switch", branch_name]
        )

    def branch_select_remote(self, branch_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "switch", "--track", branch_name]
        )

    def branch_local(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "for-each-ref", "--format=%(refname:short)", "refs/heads/"]
        )

    def branch_remote(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "for-each-ref", "--format=%(refname:short)", "refs/remotes/"]
        )

    def add(self, path: str = ".") -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "add", path]
        )

    def commit(self, message: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "commit", "-m", message]
        )

    def fetch(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "fetch", "--prune"]
        )

    def pull(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "pull"]
        )

    def push(self, branch_name: str, force: bool = False) -> Result:
        cmd = ["git", "-C", self.repo_path, "push", "origin", branch_name]
        if force:
            cmd.append("--force-with-lease")
        return self.__run_command(command=cmd)

    def reset(self, commit_id: str, reset_mode: str = "soft") -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "reset", f"--{reset_mode}", commit_id]
        )

    def log(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "log", "--oneline", "--decorate"]
        )

    def merge(self, branch_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "merge", branch_name]
        )

    def remote_list(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "remote"]
        )

    def remote_add(self, remote_name: str, remote_url: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "remote", "add", remote_name, remote_url]
        )

    def remote_remove(self, remote_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "remote", "remove", remote_name]
        )

    def cherry_pick(self, commit_id: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "cherry-pick", commit_id]
        )

    def tag_list(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag"]
        )

    def tag_create(self, tag_name: str, message: str = None) -> Result:
        if message:
            return self.__run_command(
                command=["git", "-C", self.repo_path, "tag", "-a", tag_name, "-m", message]
            )
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag", tag_name]
        )

    def tag_delete(self, tag_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag", "-d", tag_name]
        )

    def tag_push(self, tag_name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "push", "origin", tag_name]
        )

    @staticmethod
    def init(path: str) -> Result:
        try:
            result = subprocess.run(
                ["git", "init", "-b", "main", path],
                capture_output=True,
                text=True,
                timeout=20,
                check=True
            )
            return Result(stdout=result.stdout)
        except subprocess.TimeoutExpired as e:
            return Result(stdout=None, ok=False, error=str(e))
        except subprocess.CalledProcessError as e:
            return Result(stdout=None, ok=False, error=(e.stderr or e.stdout or "").strip())
        except FileNotFoundError as e:
            return Result(stdout=None, ok=False, error=f"git executable not found: {e}")

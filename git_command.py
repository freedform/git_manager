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
                error=e.stderr.strip()
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

    def branch_select_remote(self, remote_branch: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "switch", "--track", remote_branch]
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

    def reset(self, commit: str, mode: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "reset", f"--{mode}", commit]
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

    def remote_add(self, name: str, url: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "remote", "add", name, url]
        )

    def remote_remove(self, name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "remote", "remove", name]
        )

    def cherry_pick(self, commit: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "cherry-pick", commit]
        )

    def tag_list(self) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag"]
        )

    def tag_create(self, name: str, message: str = None) -> Result:
        if message:
            return self.__run_command(
                command=["git", "-C", self.repo_path, "tag", "-a", name, "-m", message]
            )
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag", name]
        )

    def tag_delete(self, name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "tag", "-d", name]
        )

    def tag_push(self, name: str) -> Result:
        return self.__run_command(
            command=["git", "-C", self.repo_path, "push", "origin", name]
        )

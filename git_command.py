import subprocess
from result import Result

class GitCommand:
    @staticmethod
    def __run_command(command: list) -> Result:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            print(f"Raw result: '{result.stdout}'")
            return Result(
                result=result.stdout
            )
        
        except subprocess.TimeoutExpired as timeout_exception:
            return Result(
                result=None,
                status="failed",
                error=timeout_exception,
            )

        except subprocess.CalledProcessError as e:
            return Result(
                result=None,
                status="failed",
                error=e.stderr.strip()
            )

    @staticmethod
    def status(repo_path: str) -> str:
        output = GitCommand.__run_command(
            command=["git", "-C", repo_path, "status", "--porcelain"]
        )
        return output.lines

    @staticmethod
    def current_branch(repo_path: str) -> str:
        result = GitCommand.__run_command(
            command=["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"]
        )
        branch = result.result.strip()
        return "DETACHED" if branch == "HEAD" else branch
    

    @staticmethod
    def branch_create(repo_path: str, branch_name: str):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "branch", branch_name]
        )
    
    @staticmethod
    def branch_delete(repo_path: str, branch_name: str):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "branch", "-D", branch_name]
        )
    
    @staticmethod
    def branch_select(repo_path: str, branch_name: str):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "switch", branch_name]
        )

    @staticmethod
    def branch_local(repo_path: str):
        output = GitCommand.__run_command(
            command=["git", "-C", repo_path, "for-each-ref", "--format=%(refname:short)", "refs/heads/"]
        )

        if not output.result or output.result.startswith("ERROR"):
            return output.lines

        return output.lines


    @staticmethod
    def branch_remote(repo_path: str):
        output = GitCommand.__run_command(
            command=["git", "-C", repo_path, "for-each-ref", "--format=%(refname:short)", "refs/remotes/"]
        )

        if not output.result or output.result.startswith("ERROR"):
            return output.lines

        return output.lines

    @staticmethod
    def add(repo_path: str, path: str = "."):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "add", path]
        )

    @staticmethod
    def commit(repo_path: str, message: str):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "commit", "-m", message]
        )

    @staticmethod
    def pull(repo_path: str):
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "pull"]
        )

    @staticmethod
    def push(repo_path: str):
        current_branch = GitCommand.current_branch(repo_path=repo_path)
        return GitCommand.__run_command(
            command=["git", "-C", repo_path, "push", "origin", current_branch]
        )

    # def merge(repo_path: str) -> str:
    # def cherry_pick(repo_path: str) -> str:
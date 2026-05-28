from git_command import GitCommand
import questionary


class GitMenu:
    def __init__(self, repo_dir_path):
        self.repo_dir_path = repo_dir_path
    
    def dispatch(self, method_name, *args, **kwargs):
        method = getattr(self, f"_{method_name}", None)
        if method is None:
            raise ValueError(f"Method '{method_name}' does not exist")

        if not callable(method):
            raise ValueError(f"Attribute '{method_name}' is not callable")

        return method(*args, **kwargs)

    
    def _status(self):
        return GitCommand.status(repo_path=self.repo_dir_path)

    def _branch_create(self):
        branch_name = questionary.text(message="Type branch name for create").ask()
        return GitCommand.branch_create(
            repo_path=self.repo_dir_path,
            branch_name=branch_name
        )

    def _branch_delete(self):
        local_branches = self._branch_local()
        selected_branch = questionary.select(message="Choose branch name to delete", choices=local_branches).ask()
        return GitCommand.branch_delete(
            repo_path=self.repo_dir_path,
            branch_name=selected_branch
        )

    def _branch_select(self):
        local_branches = self._branch_local()
        selected_branch = questionary.select(message="Choose branch name to switch", choices=local_branches).ask()
        return GitCommand.branch_select(
            repo_path=self.repo_dir_path,
            branch_name=selected_branch
        )

    def _branch_local(self):
        return GitCommand.branch_local(repo_path=self.repo_dir_path)

    def _branch_remote(self):
        return GitCommand.branch_remote(repo_path=self.repo_dir_path)

    def _add(self):
        return GitCommand.add(repo_path=self.repo_dir_path)
    
    def _commit(self):
        commit_message = questionary.text(message="Type commit message").ask()
        return GitCommand.commit(
            repo_path=self.repo_dir_path,
            message=commit_message,
        )
    def _pull(self):
        return GitCommand.pull(repo_path=self.repo_dir_path)

    def _push(self):
        return GitCommand.push(repo_path=self.repo_dir_path)
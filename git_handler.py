from pathlib import Path
import questionary
from git_command import GitCommand


class GitMenu:
    def __init__(self, repo_dir_path: str) -> None:
        self.repo_dir_path = repo_dir_path
        self.git = GitCommand(repo_dir_path)

    def __str__(self) -> str:
        branch_result = self.git.current_branch()
        branch = branch_result.stdout.strip() if branch_result.ok and branch_result.stdout else "unknown"
        return f"Repository: {Path(self.repo_dir_path).name}  |  Branch: {branch}"

    def get_actions(self, prefix: str = "_git_") -> list[str]:
        return [
            name[len(prefix):]
            for name in type(self).__dict__
            if name.startswith(prefix)
        ] + ["<< back"]

    def dispatch(self, method_name: str, *args, **kwargs) -> None:
        method = getattr(self, f"_git_{method_name}", None)
        if method is None:
            raise ValueError(f"Method '{method_name}' does not exist")
        return method(*args, **kwargs)

    def _paginate(self, lines: list[str], page_size: int = 20) -> None:
        for i in range(0, len(lines), page_size):
            print("\n".join(lines[i:i + page_size]))
            if i + page_size < len(lines):
                cont = questionary.confirm(
                    message=f"Showing {i + page_size}/{len(lines)} — continue?",
                    default=True,
                ).ask()
                if not cont:
                    break

    def _run_submenu(self, prefix: str) -> None:
        full_prefix = f"_sub_{prefix}_"
        actions = self.get_actions(full_prefix)
        while True:
            action = questionary.select(message=f"Select {prefix} action", choices=actions).ask()
            if action == "<< back":
                break
            getattr(self, f"{full_prefix}{action}")()

    def _git_status(self) -> list[str]:
        result = self.git.status()
        if not result.ok:
            print(f"Error: {result.error}")
            return []
        if not result.lines:
            print("Working tree clean.")
            return []
        print("\n".join(result.lines))
        return [line[3:] for line in result.lines]

    def _git_add(self) -> None:
        files = self._git_status()
        if not files:
            return
        selected = questionary.checkbox(message="Select files to stage", choices=["all"] + files).ask()
        if not selected:
            return
        if "all" in selected:
            result = self.git.add()
            if not result.ok:
                print(f"Error: {result.error}")
            return
        for file in selected:
            result = self.git.add(path=file)
            if not result.ok:
                print(f"Error: {result.error}")

    def _git_commit(self) -> None:
        commit_message = questionary.text(message="Type commit message").ask()
        if not commit_message:
            commit_message = "Auto commit"
        result = self.git.commit(message=commit_message)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_push(self) -> None:
        branch_result = self.git.current_branch()
        if not branch_result.ok or not branch_result.stdout:
            print("Error: Could not determine current branch")
            return
        branch = branch_result.stdout.strip()
        if branch == "HEAD":
            print("Error: Cannot push in detached HEAD state")
            return
        result = self.git.push(branch_name=branch)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_push_force(self) -> None:
        branch_result = self.git.current_branch()
        if not branch_result.ok or not branch_result.stdout:
            print("Error: Could not determine current branch")
            return
        branch = branch_result.stdout.strip()
        if branch == "HEAD":
            print("Error: Cannot push in detached HEAD state")
            return
        result = self.git.push(branch_name=branch, force=True)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_pull(self) -> None:
        result = self.git.pull()
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_history(self) -> None:
        self._run_submenu("history")

    def _sub_history_log(self) -> None:
        result = self.git.log()
        if not result.ok:
            print(f"Error: {result.error}")
            return
        if result.lines:
            self._paginate(result.lines)
        else:
            print("No commits yet.")

    def _sub_history_reset(self) -> None:
        commit = questionary.text(message="Commit ID to reset to").ask()
        if not commit:
            return
        mode = questionary.select(message="Reset mode", choices=["soft", "hard"]).ask()
        result = self.git.reset(commit=commit, mode=mode)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_branch(self) -> None:
        self._run_submenu("branch")

    def _sub_branch_create(self) -> None:
        branch_name = questionary.text(message="Type branch name for create").ask()
        result = self.git.branch_create(branch_name=branch_name)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_branch_delete(self) -> None:
        branch_result = self.git.branch_local()
        if not branch_result.ok:
            print(f"Error: {branch_result.error}")
            return
        selected_branch = questionary.select(message="Choose branch to delete", choices=branch_result.lines + ["<< back"]).ask()
        if not selected_branch or selected_branch == "<< back":
            return
        result = self.git.branch_delete(branch_name=selected_branch)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_branch_local(self) -> None:
        branch_result = self.git.branch_local()
        if not branch_result.ok:
            print(f"Error: {branch_result.error}")
            return
        selected = questionary.autocomplete(message="Choose branch to switch to", choices=branch_result.lines + ["<< back"]).ask()
        if not selected or selected == "<< back":
            return
        result = self.git.branch_select(branch_name=selected)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_branch_remote(self) -> None:
        fetch_result = self.git.fetch()
        if not fetch_result.ok:
            print(f"Error: {fetch_result.error}")
            return
        branch_result = self.git.branch_remote()
        if not branch_result.ok:
            print(f"Error: {branch_result.error}")
            return
        branches = [b for b in branch_result.lines if not b.endswith("/HEAD")]
        selected = questionary.autocomplete(message="Choose remote branch to checkout", choices=branches + ["<< back"]).ask()
        if not selected or selected == "<< back":
            return
        result = self.git.branch_select_remote(remote_branch=selected)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_cherry_pick(self) -> None:
        commit = questionary.text(message="Commit ID to cherry-pick").ask()
        if not commit:
            return
        result = self.git.cherry_pick(commit=commit)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_merge(self) -> None:
        current_result = self.git.current_branch()
        if not current_result.ok or not current_result.stdout:
            print("Error: Could not determine current branch")
            return
        current = current_result.stdout.strip()
        branch_result = self.git.branch_local()
        if not branch_result.ok:
            print(f"Error: {branch_result.error}")
            return
        candidates = [b for b in branch_result.lines if b != current]
        if not candidates:
            print("No other branches to merge from.")
            return
        source = questionary.select(message=f"Merge into '{current}' from", choices=candidates + ["<< back"]).ask()
        if not source or source == "<< back":
            return
        result = self.git.merge(branch_name=source)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_remote(self) -> None:
        self._run_submenu("remote")

    def _sub_remote_list(self) -> None:
        result = self.git.remote_list()
        if not result.ok:
            print(f"Error: {result.error}")
            return
        print("\n".join(result.lines) if result.lines else "No remotes configured.")

    def _sub_remote_add(self) -> None:
        name = questionary.text(message="Remote name").ask()
        url = questionary.text(message="Remote URL").ask()
        result = self.git.remote_add(name=name, url=url)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_remote_remove(self) -> None:
        remotes_result = self.git.remote_list()
        if not remotes_result.ok:
            print(f"Error: {remotes_result.error}")
            return
        if not remotes_result.lines:
            print("No remotes configured.")
            return
        selected = questionary.select(message="Choose remote to remove", choices=remotes_result.lines).ask()
        result = self.git.remote_remove(name=selected)
        if not result.ok:
            print(f"Error: {result.error}")

    def _git_tags(self) -> None:
        self._run_submenu("tags")

    def _sub_tags_list(self) -> None:
        result = self.git.tag_list()
        if not result.ok:
            print(f"Error: {result.error}")
            return
        print("\n".join(result.lines) if result.lines else "No tags found.")

    def _sub_tags_create(self) -> None:
        name = questionary.text(message="Tag name").ask()
        if not name:
            return
        kind = questionary.select(message="Tag type", choices=["lightweight", "annotated"]).ask()
        message = None
        if kind == "annotated":
            message = questionary.text(message="Tag message").ask()
        result = self.git.tag_create(name=name, message=message)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_tags_delete(self) -> None:
        tags_result = self.git.tag_list()
        if not tags_result.ok:
            print(f"Error: {tags_result.error}")
            return
        if not tags_result.lines:
            print("No tags found.")
            return
        selected = questionary.select(message="Choose tag to delete", choices=tags_result.lines).ask()
        result = self.git.tag_delete(name=selected)
        if not result.ok:
            print(f"Error: {result.error}")

    def _sub_tags_push(self) -> None:
        tags_result = self.git.tag_list()
        if not tags_result.ok:
            print(f"Error: {tags_result.error}")
            return
        if not tags_result.lines:
            print("No tags found.")
            return
        selected = questionary.select(message="Choose tag to push", choices=tags_result.lines).ask()
        result = self.git.tag_push(name=selected)
        if not result.ok:
            print(f"Error: {result.error}")

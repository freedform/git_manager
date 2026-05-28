import questionary
from pathlib import Path
from git_handler import GitMenu
from status import MainStatus
from cli import CLI


def find_git_repos(base_path: str) -> dict:
    base = Path(base_path)
    repos = {}

    for path in base.rglob('*'):
        if path.name == '.git':
            repos[path.parent.name] = path.parent.as_posix()

    return repos

def run_repo_menu(repo_dir_path: str) -> None:
    git_menu = GitMenu(repo_dir_path=repo_dir_path)
    while True:
        print(f"{repo_dir_path=}")
        repo_action = questionary.select(message="Select the action", choices=repo_menu.keys()).ask()

        if repo_action == "exit":
            print("exiting...")
            break
        git_menu.dispatch(repo_action)

def main():
    cli = CLI()
    cli_args = cli.parse()
    main_status = MainStatus(
        base_dir=cli_args.base_dir,
    )
    while True:
        print(main_status.get_status())
        main_action = questionary.select(message="Select the action", choices=main_menu.keys()).ask()
        
        if main_action == "exit":
            print("exiting...")
            break
        elif main_action == "select_base_directory":
            main_status.base_dir = questionary.path(message="Set base file path").ask()
            main_status.repo_list = find_git_repos(main_status.base_dir)
        elif main_action == "scan_base_directory":
            main_status.repo_list = find_git_repos(main_status.base_dir)
        elif main_action == "select_repository":
            if main_status.get_status()["found_repositories"] == 0:
                print(f"Nothing to select in {main_status.base_dir}")
                continue
            select_repo = questionary.select(message="Select git repository", choices=main_status.repo_list.keys()).ask()
            run_repo_menu(repo_dir_path=main_status.repo_list[select_repo])
        else:
            raise Exception("Unknown action in main menu")
    

main_menu = {
    "select_base_directory": {},
    "select_repository": {},
    "scan_base_directory": {},
    "exit": {},
}
repo_menu = {
    "status": {},
    "branch_create": {},
    "branch_delete": {},
    "branch_select": {},
    "branch_local": {},
    "branch_remote": {},
    "add": {},
    "commit": {},
    "pull": {},
    "push": {},
    "exit": {}
}

if __name__ == "__main__":
    main()

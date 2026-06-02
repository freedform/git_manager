import questionary
from pathlib import Path
from git_handler import GitMenu
from status import MainStatus
from cli import parse_args


def find_git_repos(base_path: str) -> dict:
    base = Path(base_path)
    repos = {}

    for path in base.rglob('.git'):
        if path.is_dir():
            repos[path.parent.name] = path.parent.as_posix()

    return repos


def run_repo_menu(repo_dir_path: str) -> None:
    git_menu = GitMenu(repo_dir_path=repo_dir_path)
    while True:
        print(git_menu)
        repo_action = questionary.select(message="Select the action", choices=git_menu.get_actions()).ask()

        if repo_action == "exit":
            print("exiting...")
            break
        git_menu.dispatch(repo_action)


def main():
    args = parse_args()
    main_status = MainStatus(base_dir=args.base_dir)
    actions = [
        "select_base_directory",
        "scan_base_directory",
        "select_repository",
        "exit",
    ]
    while True:
        print(main_status)
        main_action = questionary.select(message="Select the action", choices=actions).ask()

        if main_action == "exit":
            print("exiting...")
            break
        elif main_action == "select_base_directory":
            main_status.base_dir = questionary.path(message="Set base file path").ask()
        elif main_action == "scan_base_directory":
            main_status.repos = find_git_repos(main_status.base_dir)
        elif main_action == "select_repository":
            if not main_status.repos:
                print(f"Nothing to select in {main_status.base_dir}")
                continue
            select_repo = questionary.select(message="Select git repository", choices=main_status.repos.keys()).ask()
            run_repo_menu(repo_dir_path=main_status.repos[select_repo])


if __name__ == "__main__":
    main()
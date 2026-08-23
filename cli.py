import argparse
from git_cli import add_arguments


def parse_args():
    parser = argparse.ArgumentParser(description="Git repository manager")
    parser.add_argument(
        "--base_dir",
        type=str,
        default=".",
        help="Base directory to scan for git repositories",
    )
    parser.add_argument(
        "--mode",
        dest="app_mode",
        choices=["ui", "cli"],
        default="ui",
        help="Run mode: 'ui' for the interactive menu (default) or 'cli' for a single non-interactive "
             "action via -a/--action. Must be given explicitly to use CLI mode.",
    )
    add_arguments(parser)
    return parser.parse_args()

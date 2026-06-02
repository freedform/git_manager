import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Git repository manager")
    parser.add_argument(
        "--base_dir",
        type=str,
        default=".",
        help="Base directory to scan for git repositories",
    )
    return parser.parse_args()

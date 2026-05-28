
import argparse


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="GIT manager cli arguments"
        )

        self._build_arguments()

    def _build_arguments(self):
        # Positional argument

        # Optional argument
        self.parser.add_argument(
            "--base_dir",
            type=str,
            default=".",
            help="SSH port"
        )

    def parse(self):
        return self.parser.parse_args()
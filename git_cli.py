import argparse
import inspect

from git_command import GitCommand


def _iter_public_methods():
    for name in sorted(dir(GitCommand)):
        if name.startswith("_"):
            continue
        member = getattr(GitCommand, name)
        if inspect.isfunction(member):
            yield name, member


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add a flat, action-based CLI to `parser`: -a/--action picks which
    GitCommand method to run, -d/--directory is the target repo, and one flag
    per distinct GitCommand parameter (several methods share a flag -- see
    each help string below). All of these are optional at the argparse level
    even where a given action requires them, since the same flag can be
    required for one action and optional for another (e.g. --message is
    required for commit but optional for tag_create); run() resolves actual
    per-action requiredness against the selected method's own signature.
    Omitting -a falls back to the interactive menu."""
    action_choices = [name for name, _ in _iter_public_methods()]
    parser.add_argument("-a", "--action", choices=action_choices, help="GitCommand action to run")
    parser.add_argument("-d", "--directory", help="Path to the target git repository (not needed for init)")

    parser.add_argument(
        "--path", default=None,
        help="File to stage, relative to the repo (add, default '.'); or directory to create (init)",
    )
    parser.add_argument(
        "--branch-name", default=None,
        help="Branch name: new branch (branch_create); branch to delete/switch to (branch_delete/branch_select); "
             "branch to push (push); branch to merge from (merge)",
    )
    parser.add_argument(
        "--remote-branch", default=None,
        help="Remote-tracking branch to check out, e.g. 'origin/feature' (branch_select_remote)",
    )
    parser.add_argument(
        "--commit", default=None,
        help="Commit to reset to (reset); or commit to cherry-pick (cherry_pick)",
    )
    parser.add_argument(
        "-m", "--message", default=None,
        help="Commit message (commit, required); or tag annotation message (tag_create, optional -- omit for a "
             "lightweight tag)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force-push with lease (push)",
    )
    parser.add_argument(
        "--name", default=None,
        help="Remote name (remote_add, remote_remove); or tag name (tag_create, tag_delete, tag_push)",
    )
    parser.add_argument(
        "--url", default=None,
        help="Remote URL (remote_add)",
    )
    parser.add_argument(
        "--reset-mode", dest="mode", choices=["soft", "hard"], default=None,
        help="Reset mode (reset)",
    )


# GitCommand parameter name -> external flag, for parameters whose flag
# doesn't just match "--" + name.replace("_", "-") (currently only "mode",
# spelled --reset-mode to avoid clashing with the top-level --mode ui/cli
# switch in cli.py).
_FLAG_OVERRIDES = {"mode": "--reset-mode"}


def run(args: argparse.Namespace) -> int:
    """Dispatch a parsed -a/--action straight to GitCommand and print the Result."""
    member = getattr(GitCommand, args.action)
    params = inspect.signature(member).parameters

    kwargs = {}
    for param_name, param in params.items():
        if param_name == "self":
            continue
        value = getattr(args, param_name, None)
        if value is None:
            if param.default is inspect.Parameter.empty:
                flag = _FLAG_OVERRIDES.get(param_name, "--" + param_name.replace("_", "-"))
                print(f"Error: {flag} is required for action '{args.action}'")
                return 1
            continue
        kwargs[param_name] = value

    if "self" in params:
        if not args.directory:
            print(f"Error: --directory is required for action '{args.action}'")
            return 1
        result = getattr(GitCommand(args.directory), args.action)(**kwargs)
    else:
        result = member(**kwargs)

    if result.ok:
        if result.stdout:
            print(result.stdout.strip())
        return 0

    print(f"Error: {result.error}")
    return 1

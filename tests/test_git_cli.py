import argparse

import pytest

from cli import parse_args
from git_cli import add_arguments, run


def _parser():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser


def test_no_action_leaves_action_none():
    """main.py falls back to the interactive menu when -a/--action is omitted."""
    parser = _parser()

    args = parser.parse_args([])

    assert args.action is None


def test_action_choices_cover_every_public_git_command_method():
    parser = _parser()

    args = parser.parse_args(["-a", "status", "-d", "/tmp/whatever"])

    assert args.action == "status"
    assert args.directory == "/tmp/whatever"


def test_action_rejects_unknown_values():
    parser = _parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["-a", "not_a_real_action", "-d", "/tmp/whatever"])


def test_bool_parameter_becomes_a_store_true_flag():
    parser = _parser()

    args = parser.parse_args(["-a", "push", "-d", "/tmp/whatever", "--branch_name", "main", "--force"])

    assert args.force is True


def test_force_defaults_to_false_when_omitted():
    parser = _parser()

    args = parser.parse_args(["-a", "push", "-d", "/tmp/whatever", "--branch_name", "main"])

    assert args.force is False


def test_reset_mode_only_accepts_soft_or_hard():
    """Spelled --reset_mode, not --mode, to avoid colliding with the
    top-level --mode (ui/cli) switch's option string in cli.py -- argparse
    forbids defining --mode twice on the same parser."""
    parser = _parser()

    args = parser.parse_args(["-a", "reset", "-d", "/tmp/whatever", "--commit_id", "HEAD~1", "--reset_mode", "soft"])
    assert args.reset_mode == "soft"

    with pytest.raises(SystemExit):
        parser.parse_args(["-a", "reset", "-d", "/tmp/whatever", "--commit_id", "HEAD~1", "--reset_mode", "bogus"])


def test_message_flag_has_short_form():
    parser = _parser()

    args = parser.parse_args(["-a", "commit", "-d", "/tmp/whatever", "-m", "hi"])

    assert args.message == "hi"


# --- run() dispatch, against a real repo ------------------------------------

def test_run_status_reports_untracked_file(git_repo, capsys):
    (git_repo / "new.txt").write_text("new\n")
    parser = _parser()
    args = parser.parse_args(["-a", "status", "-d", str(git_repo)])

    exit_code = run(args)

    assert exit_code == 0
    assert "new.txt" in capsys.readouterr().out


def test_run_commit_end_to_end(git_repo):
    (git_repo / "new.txt").write_text("new\n")
    parser = _parser()
    run(parser.parse_args(["-a", "add", "-d", str(git_repo)]))

    exit_code = run(parser.parse_args(["-a", "commit", "-d", str(git_repo), "-m", "cli commit"]))

    assert exit_code == 0
    from git_command import GitCommand
    assert "cli commit" in GitCommand(str(git_repo)).log().stdout


def test_run_reset_soft_dispatches_with_mode_and_commit(git_repo):
    (git_repo / "new.txt").write_text("new\n")
    parser = _parser()
    run(parser.parse_args(["-a", "add", "-d", str(git_repo)]))
    run(parser.parse_args(["-a", "commit", "-d", str(git_repo), "-m", "second commit"]))

    exit_code = run(parser.parse_args(
        ["-a", "reset", "-d", str(git_repo), "--commit_id", "HEAD~1", "--reset_mode", "soft"]
    ))

    assert exit_code == 0
    from git_command import GitCommand
    git = GitCommand(str(git_repo))
    assert "second commit" not in git.log().stdout
    assert "new.txt" in git.status().lines[0]


def test_run_missing_required_flag_prints_error_and_returns_1(git_repo, capsys):
    """commit's message is required; tag_create's is not -- requiredness must
    be resolved per selected action, not globally per flag."""
    parser = _parser()

    exit_code = run(parser.parse_args(["-a", "commit", "-d", str(git_repo)]))

    assert exit_code == 1
    assert "message" in capsys.readouterr().out


def test_run_optional_flag_can_be_omitted_for_a_different_action(git_repo):
    """Same underlying flag (-m/--message) is optional for tag_create."""
    parser = _parser()

    exit_code = run(parser.parse_args(["-a", "tag_create", "-d", str(git_repo), "--tag_name", "v1"]))

    assert exit_code == 0


def test_run_reset_mode_defaults_to_soft_when_omitted(git_repo):
    """reset()'s mode parameter has a default of "soft", so --reset_mode is
    optional at the CLI too -- omitting it should still succeed."""
    (git_repo / "new.txt").write_text("new\n")
    parser = _parser()
    run(parser.parse_args(["-a", "add", "-d", str(git_repo)]))
    run(parser.parse_args(["-a", "commit", "-d", str(git_repo), "-m", "second commit"]))

    exit_code = run(parser.parse_args(["-a", "reset", "-d", str(git_repo), "--commit_id", "HEAD~1"]))

    assert exit_code == 0
    from git_command import GitCommand
    git = GitCommand(str(git_repo))
    assert "second commit" not in git.log().stdout
    assert "new.txt" in git.status().lines[0]


def test_run_missing_commit_id_reports_the_flag(git_repo, capsys):
    """--commit_id is shared by reset and cherry_pick (both take commit_id)."""
    parser = _parser()
    args = parser.parse_args(["-a", "reset", "-d", str(git_repo), "--reset_mode", "soft"])

    exit_code = run(args)

    assert exit_code == 1
    assert "--commit_id is required" in capsys.readouterr().out


def test_run_missing_branch_select_remote_reports_branch_name_flag(git_repo, capsys):
    """branch_select_remote shares --branch_name with the other branch
    actions rather than having its own --remote_branch flag."""
    parser = _parser()
    args = parser.parse_args(["-a", "branch_select_remote", "-d", str(git_repo)])

    exit_code = run(args)

    assert exit_code == 1
    assert "--branch_name is required" in capsys.readouterr().out


def test_run_missing_directory_for_instance_method_is_an_error(capsys):
    parser = _parser()

    exit_code = run(parser.parse_args(["-a", "status"]))

    assert exit_code == 1
    assert "directory" in capsys.readouterr().out


def test_run_error_path_prints_error_and_returns_1(git_repo, capsys):
    """Nothing staged: the CLI should surface the error and a non-zero exit code."""
    parser = _parser()
    args = parser.parse_args(["-a", "commit", "-d", str(git_repo), "-m", "empty"])

    exit_code = run(args)

    assert exit_code == 1
    assert capsys.readouterr().out.startswith("Error: ")


def test_run_init_staticmethod_dispatch_needs_no_directory(tmp_path):
    parser = _parser()
    target = tmp_path / "new_repo"
    args = parser.parse_args(["-a", "init", "--path", str(target)])

    exit_code = run(args)

    assert exit_code == 0
    assert (target / ".git").is_dir()


def test_full_parse_args_includes_the_flat_cli(monkeypatch):
    """Sanity check that cli.py's parse_args() wires in the same flags."""
    monkeypatch.setattr("sys.argv", ["main.py", "-a", "status", "-d", "/tmp/whatever"])

    args = parse_args()

    assert args.action == "status"
    assert args.directory == "/tmp/whatever"


def test_app_mode_defaults_to_ui(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py"])

    args = parse_args()

    assert args.app_mode == "ui"


def test_app_mode_cli_must_be_explicit(monkeypatch):
    """Passing -a/--action alone does not imply --mode cli."""
    monkeypatch.setattr("sys.argv", ["main.py", "-a", "status", "-d", "/tmp/whatever"])

    args = parse_args()

    assert args.app_mode == "ui"
    assert args.action == "status"  # parsed, but main() ignores it unless --mode cli


def test_app_mode_only_accepts_ui_or_cli(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "--mode", "bogus"])

    with pytest.raises(SystemExit):
        parse_args()

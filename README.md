# git_manager

A small interactive git repository manager, with a non-interactive CLI mode for scripting.

## Setup

```
source /home/ilgizs/projects/pyenvs/cli_interface/bin/activate
pip install -r requirements.txt
python main.py --base_dir <path>
```

`--base_dir` defaults to `.` if omitted — it's the directory the interactive menu scans for git repositories (`--mode ui`, see below).

## Modes

`--mode` selects `ui` (default) or `cli`:

- **`ui`** (default) — fully interactive, questionary-driven menus: pick a base directory, scan it for git repos, select one, and run git actions through prompts. Must be run in a terminal.
- **`cli`** — a single non-interactive action, for scripting. Must be requested explicitly with `--mode cli`; passing `-a/--action` alone does *not* switch modes.

```
python main.py                                  # interactive menu
python main.py --mode cli -a status -d ./repo    # one-shot, scriptable
```

## CLI mode

```
python main.py --mode cli -a <action> -d <path to repo> [flags...]
```

`-d/--directory` is required for every action except `init` (which creates a repo, so it takes `--path` instead).

Run `python main.py --help` for the full, current flag list — it's generated from `GitCommand`'s actual method signatures, so it never drifts from what the code supports. The table below is a quick reference; several actions share a flag.

| Action | Required flags | Optional flags |
|---|---|---|
| `status` | `-d` | |
| `current_branch` | `-d` | |
| `add` | `-d` | `--path` (default `.`) |
| `commit` | `-d`, `-m/--message` | |
| `fetch` | `-d` | |
| `pull` | `-d` | |
| `push` | `-d`, `-b/--branch_name` | `-f/--force` |
| `log` | `-d` | |
| `branch_create` | `-d`, `-b/--branch_name` | |
| `branch_delete` | `-d`, `-b/--branch_name` | |
| `branch_select` | `-d`, `-b/--branch_name` | |
| `branch_select_remote` | `-d`, `-b/--branch_name` (e.g. `origin/feature`) | |
| `branch_local` | `-d` | |
| `branch_remote` | `-d` | |
| `merge` | `-d`, `-b/--branch_name` | |
| `reset` | `-d`, `-c/--commit_id` | `--reset_mode` (`soft`/`hard`, default `soft`) |
| `cherry_pick` | `-d`, `-c/--commit_id` | |
| `remote_list` | `-d` | |
| `remote_add` | `-d`, `-r/--remote_name`, `-u/--remote_url` | |
| `remote_remove` | `-d`, `-r/--remote_name` | |
| `tag_list` | `-d` | |
| `tag_create` | `-d`, `-t/--tag_name` | `-m/--message` (annotated tag; omit for lightweight) |
| `tag_delete` | `-d`, `-t/--tag_name` | |
| `tag_push` | `-d`, `-t/--tag_name` | |
| `init` | `--path` | |

Examples:

```
python main.py --mode cli -a status -d ./repo
python main.py --mode cli -a commit -d ./repo -m "fix bug"
python main.py --mode cli -a branch_create -d ./repo -b feature
python main.py --mode cli -a push -d ./repo -b main -f
python main.py --mode cli -a reset -d ./repo -c HEAD~1 --reset_mode soft
python main.py --mode cli -a init --path ./new-repo
```

`-a/--action` runs exactly one action per invocation; chain steps by running the command more than once (e.g. from a shell script), not by passing several action names at once.

Missing a flag an action needs prints a clear error and exits non-zero, e.g.:

```
$ python main.py --mode cli -a commit -d ./repo
Error: --message is required for action 'commit'
```

## Development

```
pip install -r requirements-dev.txt
ruff check .
pytest
```

No formatter is configured. CI (GitHub Actions) runs both `ruff check .` and `pytest` on push to `main` and on every pull request.

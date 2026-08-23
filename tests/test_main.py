from main import find_git_repos


def test_finds_nested_git_repos(tmp_path):
    (tmp_path / "repo_a" / ".git").mkdir(parents=True)
    (tmp_path / "nested" / "repo_b" / ".git").mkdir(parents=True)
    (tmp_path / "not_a_repo").mkdir()

    repos = find_git_repos(str(tmp_path))

    assert set(repos) == {"repo_a", "repo_b"}
    assert repos["repo_a"] == (tmp_path / "repo_a").as_posix()
    assert repos["repo_b"] == (tmp_path / "nested" / "repo_b").as_posix()


def test_same_named_repos_in_different_dirs_are_disambiguated(tmp_path):
    (tmp_path / "a" / "repo" / ".git").mkdir(parents=True)
    (tmp_path / "b" / "repo" / ".git").mkdir(parents=True)

    repos = find_git_repos(str(tmp_path))

    assert len(repos) == 2
    assert set(repos) == {"repo (a/repo)", "repo (b/repo)"}
    assert repos["repo (a/repo)"] == (tmp_path / "a" / "repo").as_posix()
    assert repos["repo (b/repo)"] == (tmp_path / "b" / "repo").as_posix()


def test_uniquely_named_repos_keep_short_names_even_with_other_collisions_present(tmp_path):
    """Disambiguation is scoped to the colliding pair -- a third, uniquely
    named repo in the same scan isn't affected."""
    (tmp_path / "a" / "repo" / ".git").mkdir(parents=True)
    (tmp_path / "b" / "repo" / ".git").mkdir(parents=True)
    (tmp_path / "unique" / ".git").mkdir(parents=True)

    repos = find_git_repos(str(tmp_path))

    assert repos["unique"] == (tmp_path / "unique").as_posix()


def test_no_repos_found_returns_empty_dict(tmp_path):
    assert find_git_repos(str(tmp_path)) == {}

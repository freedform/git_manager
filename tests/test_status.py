from status import MainStatus


def test_defaults_to_empty_repo_dict():
    status = MainStatus()

    assert status.base_dir == ""
    assert status.repos == {}


def test_str_reports_base_dir_and_repo_count():
    status = MainStatus(base_dir="/tmp/x", repos={"a": "/tmp/x/a", "b": "/tmp/x/b"})

    assert str(status) == "Base directory: /tmp/x  |  Repositories found: 2"

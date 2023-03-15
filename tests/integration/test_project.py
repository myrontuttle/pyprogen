import time

from pyprogen import gh

host = "https://github.com"
owner = "myrontuttle"


def test_create_project():
    """
    Test that we can create a repo
    """
    name = "pyprogen_test_repo"
    desc = "[Delete me]. I'm a test repo for pyprogen"
    py_ver = "3.9"

    repo_url = gh.create_repo(name, desc)
    repo = gh.repo_name_from_url(repo_url)
    assert repo == f"{owner}/{name}"
    time.sleep(2)  # Make sure repo is ready at GitHub
    cs_id = gh.create_codespace(repo)
    time.sleep(6)  # Make sure codespace is ready at GitHub
    # gh.ssh_cs_config(cs_id)
    gh.configure_project(cs_id, name, desc)
    gh.setup_project(cs_id, name, desc, py_ver)
    gh.stop_codespace(cs_id)
    gh.delete_repo(f"{owner}/{name}")
    assert cs_id

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
    repo = gh.create_repo(name, desc)
    assert repo == f"{owner}/{name}"
    time.sleep(1)  # Make sure repo is ready at GitHub
    cs_id = gh.create_codespace(repo)
    time.sleep(5)  # Make sure codespace is ready at GitHub
    gh.stop_codespace(cs_id)

    gh.delete_repo(f"{owner}/{name}")

    assert cs_id

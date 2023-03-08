from github import Repository

from pyprogen import gh


def test_create_delete_repo():
    """
    Test that we can create a repo
    """
    name = "pyprogen_test_repo"
    desc = "[Delete me]. I'm a test repo for pyprogen"
    repo: Repository = gh.create_repo(name, desc)
    assert repo.name == name
    gh.delete_repo(name)

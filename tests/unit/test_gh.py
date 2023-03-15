import logging

from pyprogen import gh

LOGGER = logging.getLogger(__name__)


def test_get_gh_token_from_env(caplog):
    caplog.set_level(logging.WARNING)
    token = gh.get_gh_token_from_env()
    if token:
        assert True
    else:
        assert (
            "GH_TOKEN does not exist as environment variable." in caplog.text
        )


def test_repo_name_from_url():
    url = "https://github.com/myrontuttle/test"
    repo_name = gh.repo_name_from_url(url)
    assert repo_name == "myrontuttle/test"

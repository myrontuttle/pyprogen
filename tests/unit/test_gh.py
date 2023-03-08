from pyprogen import gh


def test_get_gh_token_from_env():
    assert gh.get_gh_token_from_env()

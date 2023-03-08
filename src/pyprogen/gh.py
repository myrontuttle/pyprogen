from typing import Optional

import logging
import os

from github import Github, Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

github_user = "myrontuttle"
template_name = "myrontuttle/python-codespace"


def get_gh_token_from_env() -> Optional[str]:
    """Returns Github Token if available as environment variable."""
    if "GH_TOKEN" not in os.environ:
        logger.critical(
            "GH_TOKEN does not exist as environment variable.",
        )
        logger.debug(os.environ)
    return os.getenv("GH_TOKEN")


def create_repo(name: str, desc: str) -> Repository:
    """
    Create a Github repo
    """
    token = get_gh_token_from_env()
    g = Github(token)
    template_repo = g.get_repo(template_name)
    user = g.get_user()
    repo = user.create_repo_from_template(name, template_repo, desc, False)
    return repo


def delete_repo(name: str):
    """
    Delete a Github repo
    """
    token = get_gh_token_from_env()
    g = Github(token)
    repo = g.get_repo(f"{github_user}/{name}")
    repo.delete()

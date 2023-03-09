from typing import Optional

import logging
import os
import subprocess
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

github_host = "github.com"
github_user = "myrontuttle"
template_name = "myrontuttle/python-codespace"
codespace_retention = "1h"
codespace_machine = "basicLinux32gb"


def get_gh_token_from_env() -> Optional[str]:
    """Returns Github Token if available as environment variable."""
    if "GH_TOKEN" not in os.environ:
        logger.critical(
            "GH_TOKEN does not exist as environment variable.",
        )
        logger.debug(os.environ)
    return os.getenv("GH_TOKEN")


def create_repo(name: str, desc: str) -> Optional[str]:
    """
    Create a Github repo.
    gh repo create {name} -d "{desc}" -p {template_name} --public
    Returns repo name
    """
    token = get_gh_token_from_env()
    if not token:
        return ""

    cp_create = subprocess.run(
        [
            "gh",
            "repo",
            "create",
            name,
            "-d",
            f'"{desc}"',
            "-p",
            template_name,
            "--public",
        ],
        capture_output=True,
    )
    if cp_create.returncode == 0:
        return repo_name_from_url(cp_create.stdout)
    else:
        logger.error(cp_create.stderr)
        return None


def repo_name_from_url(url: bytes) -> str:
    return urlparse(url.decode("UTF-8")).path.strip("/")


def delete_repo(name: str) -> None:
    """
    Delete a Github repo
    gh repo delete {name} --yes
    """
    token = get_gh_token_from_env()
    if not token:
        return None

    cp_auth = subprocess.run(
        [
            "gh",
            "auth",
            "refresh",
            "-h",
            github_host,
            "-s",
            "delete_repo",
        ],
        capture_output=True,
    )
    if cp_auth.returncode != 0:
        logger.warning(cp_auth.stderr)
    cp_del = subprocess.run(
        [
            "gh",
            "repo",
            "delete",
            name,
            "--yes",
        ],
        capture_output=True,
    )
    if cp_del.returncode != 0:
        logger.warning(cp_del.stderr)


def create_codespace(repo: str) -> Optional[str]:
    """
    Use Github CLI to create codespace for the repo provided
    gh codespace create -R {repo} --retention-period "1h" -m "basicLinux32gb"
    returns codespace id
    """
    cp_create = subprocess.run(
        [
            "gh",
            "codespace",
            "create",
            "-R",
            repo,
            "--retention-period",
            codespace_retention,
            "-m",
            codespace_machine,
        ],
        capture_output=True,
    )
    if cp_create.returncode == 0:
        return cp_create.stdout.decode("UTF-8").strip()
    else:
        logger.error(cp_create.stderr)
        return None


def stop_codespace(cs_id: str) -> None:
    """
    Use Github CLI to stop codespace with the id provided
    gh codespace stop -c [<cs_id>]
    """
    if not cs_id:
        logger.error("No codespace id provided to stop.")
        return None
    cp_stop = subprocess.run(
        [
            "gh",
            "codespace",
            "stop",
            "-c",
            cs_id,
        ],
        capture_output=True,
    )
    if cp_stop.returncode != 0:
        logger.error(cp_stop.stderr)

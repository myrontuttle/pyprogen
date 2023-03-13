from typing import Optional

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from fabric import Config, Connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

github_host = "github.com"
github_user = "myrontuttle"
cs_template_name = "myrontuttle/python-codespace"
codespace_retention = "1h"
codespace_machine = "basicLinux32gb"
cp_template_name = "myrontuttle/python-copier-template"


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
            cs_template_name,
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


def ssh_cs_config(cs_id: str) -> Optional[str]:
    """
    Use Github CLI to setup ssh to a codespace with the id provided
    gh codespace ssh -c [<cs_id>]
    """
    if not cs_id:
        logger.error("No codespace id provided to ssh.")
        return None
    cp_ssh = subprocess.run(
        [
            "gh",
            "codespace",
            "ssh",
            "-c",
            cs_id,
            "--config",
        ],
        capture_output=True,
    )
    if cp_ssh.returncode == 0:
        with open(f"{Path.home()}/.ssh/codespaces", "w") as file:
            file.write(
                cp_ssh.stdout.decode("UTF-8")
                .replace("codespaces.auto", "id_ed25519")
                .replace("C:\\Program Files\\GitHub CLI\\gh.exe", "gh")
            )
        with open(f"{Path.home()}/.ssh/config", "w") as file:
            file.write(f"Match all\nInclude {Path.home()}/.ssh/codespaces\n")
        return cp_ssh.stdout.decode("UTF-8")
    else:
        logger.error(cp_ssh.stderr)


def setup_project(
    cs_id: str, project_name: str, project_desc: str, py_ver: str
) -> Optional[str]:
    """
    Use Github CLI to setup project in the codespace with the id provided
    gh codespace ssh -c [<cs_id>] {command}
    """
    if not cs_id:
        logger.error("No codespace id provided to setup project.")
        return None
    gh_token = get_gh_token_from_env()
    if not gh_token:
        return None
    cp_ssh = subprocess.run(
        [
            "gh",
            "cs",
            "ssh",
            "-c",
            cs_id,
            '"export"',
            f'"GH_TOKEN={gh_token}"',
        ],
        capture_output=True,
    )
    if cp_ssh.returncode == 0:
        result_1 = subprocess.run(
            [
                "gh",
                "cs",
                "ssh",
                "-c",
                cs_id,
                '"gh"',
                '"extension"',
                '"install"',
                '"twelvelabs/gh-repo-config"',
            ],
            capture_output=True,
        )
        return result_1.stdout.decode("UTF-8")
    else:
        logger.error(cp_ssh.stderr)


def setup_project_on_cs(
    host: str, project_name: str, project_desc: str, py_ver: str
):
    """
    Run commands to setup project on codespace
    """
    gh_token = get_gh_token_from_env()
    if not gh_token:
        return ""
    conf = Config(runtime_ssh_path=f"{Path.home()}/.ssh/codespaces")
    c = Connection(host, config=conf)
    c.run(f"export GH_TOKEN={gh_token}")
    c.run("gh extension install twelvelabs/gh-repo-config")
    c.run("gh repo-config apply")
    c.run(
        f"copier gh:"
        f"{cp_template_name} ./ --data \"minimal_python_version='"
        f"{py_ver}'\" --data \"project_name='{project_name}'\" "
        f"--data \"project_description='{project_desc}'\" --force"
    )

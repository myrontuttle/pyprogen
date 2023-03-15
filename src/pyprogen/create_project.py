import time

import click

from pyprogen import gh

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("project_name")
@click.option("-d", "--description", default="")
@click.option("-pv", "--python_version", default="3.9")
def create_project(
    project_name: str, description: str = "", python_version: str = "3.9"
):
    """
    Creates a Python project with a GitHub repo and standard project files
    """
    click.echo("Creating Repo")
    repo_url = gh.create_repo(project_name, description)
    repo = gh.repo_name_from_url(repo_url)
    time.sleep(2)  # Make sure repo is ready at GitHub
    click.echo("Creating Codespace")
    cs_id = gh.create_codespace(repo)
    time.sleep(6)  # Make sure codespace is ready at GitHub
    click.echo("Configuring project")
    gh.configure_project(cs_id, project_name, description)
    click.echo("Populating project")
    gh.setup_project(cs_id, project_name, description, python_version)
    git_repo = f"git@github.com:{repo}.git"
    click.echo(f"Project available at: {repo_url} and {git_repo}")


if __name__ == "__main__":
    create_project()

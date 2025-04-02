"""
Import as:

import DATA605.TutorialsTask76_automate_collaborator_invitations_from_gsheet as dtacifrgs
"""

import logging
import subprocess
from typing import List

# Install pygithub.
subprocess.run(
    ["sudo", "/venv/bin/pip", "install", "--quiet", " pygithub"], check=True
)
import helpers.hgoogle_file_api as hgofiapi
from github import Github

_LOG = logging.getLogger(__name__)

# Globals.
DRIVE_URL = "https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0"
GH_ACCESS_TOKEN = ""
REPO_NAME = "tutorials"
ORG_NAME = "causify-ai"


def extract_usernames_from_gsheet(gsheet_url: str) -> List[str]:
    """
    Extract usernames from a Google Sheet URL.

    :param gsheet_url: URL of the Google Sheet
    :return: github usernames
    """
    credentials = hgofiapi.get_credentials(
        service_key_path="/app/DATA605/google_secret.json"
    )
    df = hgofiapi.read_google_file(url, credentials=credentials)
    usernames = df["github_username"].tolist()
    _LOG.info("Usernames = \n  %s", usernames)
    return usernames


def send_invitations(
    usernames: List[str],
    gh_access_token: str,
    repo_name: str,
    org_name: str,
) -> None:
    """
    Send GitHub collaborator invitations to given usernames.

    :param usernames: List of GitHub usernames
    :param gh_access_token: GitHub API access token
    :param repo_url: URL of the target repository
    """
    # Initialize GitHub API.
    g = Github(gh_access_token)
    # Get the repository.
    repo = g.get_repo(f"{org_name}/{repo_name}")
    # Send invitations.
    for username in usernames:
        try:
            # Send invitation by adding as collaborator.
            repo.add_to_collaborators(
                username,
                # TODO Krishna: Update the permission accordingly.
                permission="pull",
            )
            _LOG.info(f"Invitation sent to {username}")
        except Exception as e:
            _LOG.error(f"Failed to invite {username}: {str(e)}")


def main():
    # Extract usernames from Google Sheet.
    usernames = extract_usernames_from_gsheet(DRIVE_URL)
    # Send invitations.
    send_invitations(usernames, GH_ACCESS_TOKEN, REPO_NAME, ORG_NAME)


if __name__ == "__main__":
    main()

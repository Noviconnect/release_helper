import re

from github import Github, GitRelease
from loguru import logger

from release_helper.exceptions import ReleaseHelperError


class SourceControlGithub:
    def __init__(self, token: str, repository: str):
        self.client = self.get_client(token)
        self.repository = repository

    def get_client(self, token: str) -> Github:
        client = Github(token)
        return client

    def get_draft_release(self) -> GitRelease:
        logger.info("Getting data for the {} repository", self.repository)

        gh_repository = self.client.get_repo(self.repository)

        releases = gh_repository.get_releases()

        logger.info("The releases found: {}", releases)

        for release in releases:
            logger.info(
                "Found release: {} with status {}", release.title, release.draft
            )

            if release.draft and release.title.startswith("v"):
                return release

        raise ReleaseHelperError(
            message="Unable to locate a draft release that starts with 'v'."
        )

    @staticmethod
    def get_issues_from_release(release: GitRelease) -> list:
        logger.info("Looking for issues in the: {}", release)

        # Use a regular expression to find all issue identifiers in the release body
        results = re.findall(r"[a-zA-Z][a-zA-Z0-9]+-[0-9]+", release.body)

        for result in results:
            logger.info("Found: {}", result)

        return results

    @staticmethod
    def deploy(release_draft: GitRelease) -> None:
        name = release_draft.title
        tag_name = release_draft.tag_name
        message = release_draft.body
        release_draft.update_release(
            draft=False, name=name, tag_name=tag_name, message=message
        )

import logging
import os
import re

from github import Github, GitRelease

from release_helper.exceptions import ReleaseHelperError


logger = logging.getLogger(__name__)


class SourceControlGithub:
    def __init__(self):
        self.client = self.get_client()

    @staticmethod
    def get_client() -> Github:
        gh_token = os.environ.get("HELPER_GITHUB_TOKEN")
        client = Github(gh_token)
        return client

    def get_draft_release(self) -> GitRelease:
        repository = os.environ.get("GITHUB_REPOSITORY")
        logger.info("Getting data for the %s repository", repository)

        gh_repository = self.client.get_repo(repository)

        releases = gh_repository.get_releases()

        logger.info("The releases found: %s", releases)

        for release in releases:
            logger.info(
                "Found release: %s with status %s", release.title, release.draft
            )

            if release.draft and release.title.startswith("v"):
                return release

        raise ReleaseHelperError(
            message="Unable to locate a draft release that starts with 'v'."
        )

    @staticmethod
    def get_issues_from_release(release: GitRelease) -> list:
        logger.info("Looking for issues in the: %s", release)

        results = re.findall(r"[a-zA-Z][a-zA-Z0-9]+-[0-9]+", release.body)

        for result in results:
            logger.info("Found: %s", result)

        return results

    @staticmethod
    def deploy(release_draft: GitRelease) -> None:
        name = release_draft.title
        tag_name = release_draft.tag_name
        message = release_draft.body
        release_draft.update_release(
            draft=False, name=name, tag_name=tag_name, message=message
        )

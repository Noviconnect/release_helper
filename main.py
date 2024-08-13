import logging
from typing import TYPE_CHECKING

from release_helper.exceptions import ReleaseHelperError
from release_helper.issue_management.linear import IssueManagementLinear
from release_helper.messaging.slack import MessagingSlack
from release_helper.source_control.github import SourceControlGithub


if TYPE_CHECKING:
    from github import GitRelease

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_potential_release() -> None:
    github = SourceControlGithub()
    linear = IssueManagementLinear()
    slack = MessagingSlack()

    try:
        release_draft: GitRelease = github.get_draft_release()
    except ReleaseHelperError as e:
        slack.send_errors([e])
        logger.info("No draft release found. Exiting.")
        return

    issue_names = github.get_issues_from_release(release_draft)

    issues, errors = linear.get_issues(issue_names)

    slack.send_release_message(release_draft, issues)

    if len(errors) == 0:
        if all(issue.state.type == "completed" for issue in issues):
            github.deploy(release_draft)
            linear.set_issues_to_deployed(issues)
            slack.send_deploy_message(release_draft.title)
            logger.info("Release deployed.")
        else:
            slack.send_not_deploy_message(release_draft.title)
            logger.info("Not all issues are completed.")
    else:
        slack.send_errors(errors)
        logger.info("Errors found. Not deploying.")


if __name__ == "__main__":
    process_potential_release()

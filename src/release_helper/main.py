from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from release_helper.exceptions import ReleaseHelperError
from release_helper.issue_management.linear import IssueManagementLinear
from release_helper.messaging.slack import MessagingSlack
from release_helper.settings import Settings
from release_helper.source_control.github import SourceControlGithub


if TYPE_CHECKING:
    from github import GitRelease


def process_potential_release() -> None:
    settings = Settings()

    github = SourceControlGithub(
        settings.helper.github_token, settings.github_repository
    )
    linear = IssueManagementLinear(settings.helper.linear.token)
    slack = MessagingSlack(settings.helper.slack.bot_token)

    try:
        release_draft: GitRelease = github.get_draft_release()
    except ReleaseHelperError as e:
        handle_no_draft_release(slack, settings, e)
        return

    issue_names = github.get_issues_from_release(release_draft)
    issues, errors = linear.get_issues(issue_names)

    if settings.helper.deploy:
        handle_deploy(settings, slack, github, linear, release_draft, issues, errors)
    else:
        handle_non_deploy(settings, slack, issues, release_draft)


def handle_no_draft_release(
    error: ReleaseHelperError,
    settings: Settings,
    slack: MessagingSlack,
) -> None:
    slack.send_errors(channel=settings.helper.slack.deploy_channel, errors=[error])
    logger.info("No draft release found. Exiting.")


def handle_deploy(
    errors: list[Exception],
    github: SourceControlGithub,
    issues: list[IssueManagementLinear.Issue],
    linear: IssueManagementLinear,
    release_draft: GitRelease,
    settings: Settings,
    slack: MessagingSlack,
) -> None:
    if errors:
        slack.send_errors(channel=settings.helper.slack.deploy_channel, errors=errors)
        logger.info("Errors found. Not deploying. %s", errors)
        return

    if all(issue.state.type == "completed" for issue in issues):
        github.deploy(release_draft)
        linear.set_issues_to_deployed(issues)
        slack.send_deploy_message(
            channel=settings.helper.slack.deploy_channel,
            release_title=release_draft.title,
        )
        logger.info("Release deployed.")
    else:
        slack.send_release_message(
            channel=settings.helper.slack.deploy_channel,
            release_draft=release_draft,
            issues=issues,
            repository=settings.github_repository,
        )
        slack.send_not_deploy_message(
            channel=settings.helper.slack.deploy_channel,
            release_title=release_draft.title,
        )
        logger.info("Not all issues are completed. Not deploying.")


def handle_non_deploy(
    issues: list[IssueManagementLinear.Issue],
    release_draft: GitRelease,
    settings: Settings,
    slack: MessagingSlack,
) -> None:
    for issue in issues:
        if issue.state.type != "completed":
            block = slack.generate_user_message(issue)
            channel = settings.helper.slack.channels.get(
                issue.team.key.casefold(), settings.helper.slack.deploy_channel
            )
            slack.send_blocks(channel=channel, blocks=[block], text="")
            logger.info("Ticket Status messages sent.")

    slack.send_not_deploy_message(
        channel=settings.helper.slack.deploy_channel,
        release_title=release_draft.title,
    )
    logger.info("The deploy setting is '%s'. Not deploying.", settings.helper.deploy)


if __name__ == "__main__":
    process_potential_release()

from __future__ import annotations

from typing import TYPE_CHECKING

import slack_sdk.web
from loguru import logger
from slack_sdk import WebClient


if TYPE_CHECKING:
    from github.GitRelease import GitRelease

    from release_helper.exceptions import ReleaseHelperError
    from release_helper.issue_management.linear import graphql_client


class MessagingSlack:
    def __init__(self, token: str):
        self.client = self.get_client(token)

    @staticmethod
    def get_client(token: str) -> WebClient:
        return WebClient(token=token)

    def send_blocks(self, *, channel: str, blocks: list[dict], text: str) -> None:
        logger.info("Sending Slack message with {} blocks", len(blocks))

        self.client.chat_postMessage(channel=channel, blocks=blocks, text=text)

    def generate_user_message(self, issue: graphql_client.IssueIssue) -> dict[str, str]:
        issue_id = issue.identifier
        issue_title = issue.title
        issue_state = issue.state.name
        issue_url = issue.url
        issue_assignee = issue.assignee

        if issue_assignee is None:
            logger.error("Issue {} has no assignee", issue_id)

        issue_assignee_email = issue_assignee.email

        user_notification = ""

        if issue.state.type != "completed":
            slack_user: slack_sdk.web.SlackResponse = self.client.users_lookupByEmail(
                email=issue_assignee_email
            )
            slack_user_id = slack_user.data["user"]["id"]
            user_notification = f"\n\n cc: <@{slack_user_id}>"

        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{issue_url}|{issue_id}> {issue_title}\n*{issue_state}* {user_notification}",
            },
        }

        return block

    def send_release_message(
        self,
        *,
        channel: str,
        release_draft: GitRelease,
        issues: list[graphql_client.IssueIssue],
        repository: str,
    ) -> None:
        release_title = release_draft.title
        repository_full = repository
        repository_short = repository_full.split("/")[1]

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{repository_short} - Draft Release: {release_title}",
                    "emoji": True,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"<https://github.com/{repository_full}/releases|View Releases>",
                    }
                ],
            },
        ]

        for issue in issues:
            blocks.append({"type": "divider"})
            block = self.generate_user_message(issue)
            blocks.append(block)

        self.send_blocks(
            channel=channel,
            blocks=blocks,
            text=f"Release {release_title} for {repository_short}",
        )

    def send_deploy_message(self, *, channel: str, release_title: str) -> None:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All issues are in completed state - ** Deploying {release_title}**",
                },
            }
        ]

        self.send_blocks(
            channel=channel, blocks=blocks, text=f"Deploying {release_title}"
        )

    def send_not_deploy_message(self, *, channel: str, release_title: str) -> None:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All issues are NOT in completed state - **Not deploying {release_title}**",
                },
            }
        ]

        self.send_blocks(
            channel=channel, blocks=blocks, text=f"Not deploying {release_title}"
        )

    def send_errors(self, *, channel: str, errors: list[ReleaseHelperError]) -> None:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Error Processing Release",
                    "emoji": True,
                },
            }
        ]

        for error in errors:
            blocks.append({"type": "divider"})
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{error.message}*",
                    },
                }
            )

        self.send_blocks(
            channel=channel, blocks=blocks, text="Error Processing Release"
        )

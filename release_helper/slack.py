from __future__ import annotations

import os
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import graphql_client
    from github.GitRelease import GitRelease

    from release_helper.exceptions import ReleaseHelperError

import slack_sdk.web
from slack_sdk import WebClient


class MessagingSlack:
    def __init__(self):
        self.client = self.get_client()

    @staticmethod
    def get_client() -> WebClient:
        return WebClient(token=os.environ["HELPER_SLACK_BOT_TOKEN"])

    def send_blocks(self, blocks: dict[str, str]) -> None:
        self.client.chat_postMessage(
            channel=os.environ.get("HELPER_SLACK_CHANNEL_NAME"),
            blocks=blocks,
        )

    def generate_user_message(self, issue: graphql_client.IssueIssue) -> dict[str, str]:
        issue_id = issue.identifier
        issue_title = issue.title
        issue_state = issue.state.name
        issue_url = issue.url
        issue_assignee = issue.assignee
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
        self, release_draft: GitRelease, issues: list[graphql_client.IssueIssue]
    ) -> None:
        release_title = release_draft.title
        repository_full = os.environ.get("GITHUB_REPOSITORY")
        repository = os.environ.get("GITHUB_REPOSITORY").split("/")[1]

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{repository} - Draft Release: {release_title}",
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

        self.send_blocks(blocks)

    def send_deploy_message(self, release_title: str) -> None:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All issues are in completed state - ** Deploying {release_title}**",
                },
            }
        ]

        self.send_blocks(blocks)

    def send_not_deploy_message(self, release_title: str) -> None:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All issues are NOT in completed state - **Not deploying {release_title}**",
                },
            }
        ]

        self.send_blocks(blocks)

    def send_errors(self, errors: list[ReleaseHelperError]) -> None:
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

        self.send_blocks(blocks)

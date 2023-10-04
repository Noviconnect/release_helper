# Standard Library
import os
import re

# Third Party
from github import (
    Github,
    GitRelease
)
from graphql_client import (
    Client,
    IssueIssue,
    IssueUpdateInput,
    StringComparator,
    WorkflowStateFilter
)
from slack_sdk import WebClient


def get_draft_release() -> GitRelease:
    g = get_github_client()

    repository = os.environ.get("HELPER_REPOSITORY")
    print(f"Getting data for the {repository} repository")

    gh_repository = g.get_repo(repository)

    releases = gh_repository.get_releases()

    print(f"The releases found: {releases}")

    for release in releases:
        print(f"Found release: {release.title} with status {release.draft}")

        if release.draft and release.title.startswith("v"):
            return release

    raise RuntimeError("Unable to locate a draft release that starts with 'v'.")


def get_github_client():
    gh_token = os.environ.get("HELPER_GITHUB_TOKEN")
    g = Github(gh_token)
    return g


def get_issues_from_release(release: GitRelease) -> list:
    print(f"Looking for issues in the: {release}")

    results = re.findall(r"[a-zA-Z][a-zA-Z0-9]+-[0-9]+", release.body)

    for result in results:
        print(f"Found: {result}")

    return results


def get_linear_issue_status(linear_client: Client, linear_issue_id) -> IssueIssue:
    result = linear_client.issue(linear_issue_id)
    return result.issue


def get_issues(linear_client: Client, linear_issues: list) -> list[IssueIssue]:
    results = []
    for linear_issue in linear_issues:
        issue = get_linear_issue_status(linear_client, linear_issue)
        results.append(issue)

    return results


def send_slack_message(release_draft: GitRelease, issues: list[IssueIssue]):
    client = WebClient(token=os.environ["HELPER_SLACK_BOT_TOKEN"])

    release_title = release_draft.title
    release_url = release_draft.html_url

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Draft Release: {release_title}",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"<{release_url}|View Release>"}],
        },
    ]

    for issue in issues:
        blocks.append({"type": "divider"})
        block = generate_slack_user_message(client, issue)
        blocks.append(block)

    if can_auto_deploy(issues):
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All issues are in completed state - ** Deploying {release_title}**",
                },
            }
        )

    client.chat_postMessage(
        channel="#deploys",
        blocks=blocks,
    )


def generate_slack_user_message(client, issue):
    issue_id = issue.identifier
    issue_title = issue.title
    issue_state = issue.state.name
    issue_url = issue.url
    issue_assignee = issue.assignee
    issue_assignee_email = issue_assignee.email

    user_notification = ""

    if issue.state.type != "completed":
        slack_user = client.users_lookupByEmail(email=issue_assignee_email)
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


def can_auto_deploy(issues: list[IssueIssue]):
    return all(issue.state.type == "completed" for issue in issues)


def deploy(release_draft: GitRelease):
    name = release_draft.title
    tag_name = release_draft.tag_name
    message = release_draft.body
    release_draft.update_release(draft=False, name=name, tag_name=tag_name, message=message)


def get_linear_issues(linear_client: Client, issue_names):
    issues = get_issues(linear_client, issue_names)
    return issues


def get_linear_client():
    token = os.environ.get("HELPER_LINEAR_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    linear_client = Client(url="https://api.linear.app/graphql", headers=headers)
    return linear_client


def set_issues_to_deployed(linear_client: Client, issues):
    issue: IssueIssue

    for issue in issues:
        if issue.state.name == "Ready to Deploy":
            states = WorkflowStateFilter(name=StringComparator(eq="Deployed"))
            deployed_state = linear_client.state(filter=states)
            update = IssueUpdateInput(state_id=deployed_state.workflow_states.nodes[0].id)
            linear_client.issue_update(issue_id=issue.id, input=update)


def process_potential_release():
    release_draft: GitRelease = get_draft_release()

    issue_names = get_issues_from_release(release_draft)

    linear_client = get_linear_client()

    issues = get_linear_issues(linear_client, issue_names)

    send_slack_message(release_draft, issues)

    if can_auto_deploy(issues):
        deploy(release_draft)
        # Send a Slack message indicating that the deploy happened - maybe @here

        set_issues_to_deployed(linear_client, issues)


if __name__ == "__main__":
    process_potential_release()

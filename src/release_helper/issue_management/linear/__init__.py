from __future__ import annotations

import httpx

from release_helper.exceptions import IssueError, ReleaseHelperError
from release_helper.issue_management.linear.graphql_client import (
    Client,
    GraphQLClientGraphQLMultiError,
    IssueIssue,
    IssueUpdateInput,
    StringComparator,
    TeamFilter,
    WorkflowStateFilter,
)


class IssueManagementLinear:
    def __init__(self, token: str):
        self.client = self.get_client(token)

    def get_client(self, token: str) -> Client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{token}",
        }
        linear_client = Client(
            url="https://api.linear.app/graphql",
            headers=headers,
            http_client=httpx.Client(headers=headers, timeout=httpx.Timeout(30)),
        )
        return linear_client

    def get_issues(
        self, linear_issues: list[str]
    ) -> tuple[list[IssueIssue], list[ReleaseHelperError]]:
        results: list[IssueIssue] = []
        errors: list[ReleaseHelperError] = []

        for linear_issue in linear_issues:
            try:
                issue = self.get_linear_issue_status(linear_issue)
                results.append(issue)
            except ReleaseHelperError as e:  # noqa: PERF203
                errors.append(e)

        return results, errors

    def get_linear_issue_status(self, linear_issue_id: str) -> IssueIssue:
        try:
            result = self.client.issue(linear_issue_id)
        except GraphQLClientGraphQLMultiError as e:
            message = f"Error retrieving issue {linear_issue_id}"
            raise IssueError(
                message=message, issue_id=linear_issue_id, linear_exception=e
            ) from e
        else:
            return result.issue

    def set_issues_to_deployed(self, issues: list[IssueIssue]) -> None:
        issue: IssueIssue

        for issue in issues:
            if issue.state.name == "Ready to Deploy":
                team_filter = TeamFilter(key=StringComparator(eq=issue.team.key))
                states = WorkflowStateFilter(
                    name=StringComparator(eq="Deployed"), team=team_filter
                )
                deployed_state = self.client.state(filter=states)
                update = IssueUpdateInput(
                    state_id=deployed_state.workflow_states.nodes[0].id
                )
                self.client.issue_update(issue_id=issue.id, input=update)

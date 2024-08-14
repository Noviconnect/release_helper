from __future__ import annotations

import os

import httpx

from release_helper.exceptions import IssueError, ReleaseHelperError
from release_helper.issue_management.linear.graphql_client import (
    Client as GeneratedClient,
)
from release_helper.issue_management.linear.graphql_client import (
    GraphQLClientGraphQLMultiError,
    IssueIssue,
    IssueUpdateInput,
    StringComparator,
    WorkflowStateFilter,
)


class CustomClient(GeneratedClient):
    def __init__(
        self,
        url: str = "",
        headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ):
        super().__init__(url, headers, http_client)
        self.http_client = httpx.Client(headers=self.headers, timeout=httpx.Timeout(30))


class IssueManagementLinear:
    def __init__(self):
        self.client = self.get_client()

    @staticmethod
    def get_client() -> CustomClient:
        token = os.environ.get("HELPER_LINEAR_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{token}",
        }
        linear_client = CustomClient(
            url="https://api.linear.app/graphql", headers=headers
        )
        return linear_client

    def get_issues(
        self, linear_issues: list
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
            raise IssueError(e) from e
        else:
            return result.issue

    def set_issues_to_deployed(self, issues: list[IssueIssue]) -> None:
        issue: IssueIssue

        for issue in issues:
            if issue.state.name == "Ready to Deploy":
                states = WorkflowStateFilter(name=StringComparator(eq="Deployed"))
                deployed_state = self.client.state(filter=states)
                update = IssueUpdateInput(
                    state_id=deployed_state.workflow_states.nodes[0].id
                )
                self.client.issue_update(issue_id=issue.id, input=update)

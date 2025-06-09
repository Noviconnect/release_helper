from __future__ import annotations

from typing import TYPE_CHECKING

import openai
from loguru import logger


if TYPE_CHECKING:
    from release_helper.issue_management.linear import IssueManagementLinear


class OpenAIGenerator:
    def __init__(self, api_key: str, model: str):
        self.client = self.get_client(api_key)
        self.model = model

    def get_client(self, api_key: str) -> openai.Client:
        return openai.Client(api_key=api_key)

    def generate_release_notes(
        self,
        release_title: str,
        release_body: str,
        issues: list[IssueManagementLinear.Issue],
    ) -> str:
        """Generate human-readable release notes using OpenAI.

        Args:
            release_title: The title of the release
            release_body: The body/description of the release
            issues: The list of Linear issues included in the release

        Returns:
            The AI-generated release notes
        """
        logger.info(f"Generating release notes for: {release_title}")

        # Prepare the issues data
        issues_data = []
        for issue in issues:
            # Get labels if available
            labels = []
            if (
                hasattr(issue, "labels")
                and issue.labels
                and hasattr(issue.labels, "nodes")
            ):
                labels = [label.name for label in issue.labels.nodes]

            # Get project info if available
            project_info = None
            initiative_info = []
            if hasattr(issue, "project") and issue.project:
                project_info = {
                    "name": issue.project.name,
                    "description": issue.project.description,
                    "url": issue.project.url,
                }

                # Get initiatives info if available
                if (
                    hasattr(issue.project, "initiatives")
                    and issue.project.initiatives
                    and hasattr(issue.project.initiatives, "nodes")
                ):
                    initiative_info = [
                        {
                            "id": initiative.id,
                            "name": initiative.name,
                            "description": initiative.description
                            if hasattr(initiative, "description")
                            else None,
                        }
                        for initiative in issue.project.initiatives.nodes
                    ]

            # Format dates if available
            created_at = issue.createdAt if hasattr(issue, "createdAt") else None
            completed_at = issue.completedAt if hasattr(issue, "completedAt") else None

            issues_data.append(
                {
                    "identifier": issue.identifier,
                    "title": issue.title,
                    "description": issue.description
                    if hasattr(issue, "description")
                    else None,
                    "url": issue.url,
                    "state": issue.state.name,
                    "team": {
                        "key": issue.team.key,
                        "name": issue.team.name
                        if hasattr(issue.team, "name")
                        else issue.team.key,
                    },
                    "priority": issue.priority if hasattr(issue, "priority") else None,
                    "priorityLabel": issue.priorityLabel
                    if hasattr(issue, "priorityLabel")
                    else None,
                    "labels": labels,
                    "project": project_info,
                    "initiatives": initiative_info,
                    "createdAt": created_at,
                    "completedAt": completed_at,
                    "assignee": issue.assignee.name if issue.assignee else "Unassigned",
                }
            )

        # Create the prompt for OpenAI
        prompt = f"""
        You are a technical writer creating release notes for a software product.
        Your task is to create a clear, concise, and human-readable summary of the changes in this release.

        Here is the information about the release:

        Release Title: {release_title}

        Release Description:
        {release_body}

        Issues included in this release:
        {self._format_issues_for_prompt(issues_data)}

        Please create a well-structured summary of this release that:
        1. Explains the main purpose and benefits of this release
        2. Highlights key features or improvements
        3. Mentions any important bug fixes
        4. Indicates which initiatives the projects and issues support (if initiative information is available)
        5. Is written in a professional but approachable tone
        6. Is organized with clear sections
        7. Is concise (around 300-500 words)

        Do not include technical jargon without explanation. Focus on the value to users.
        Do not include the issue identifiers (like ABC-123) in your summary.
        """

        # Call the OpenAI API

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a skilled technical writer creating clear, concise release notes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        # Extract and return the generated content
        generated_content = response.choices[0].message.content.strip()
        logger.info("Successfully generated release notes")
        return generated_content

    def _format_issues_for_prompt(self, issues_data: list[dict]) -> str:
        """Format the issues data for inclusion in the prompt."""
        formatted_issues = []
        for issue in issues_data:
            # Start with basic issue info
            issue_text = f"- {issue['identifier']}: {issue['title']}"

            # Add team info
            team_info = (
                issue["team"]["name"]
                if isinstance(issue["team"], dict) and "name" in issue["team"]
                else issue["team"]
            )
            issue_text += f"\n  Team: {team_info}"

            # Add assignee
            issue_text += f"\n  Assignee: {issue['assignee']}"

            # Add priority if available
            if issue["priorityLabel"]:
                issue_text += f"\n  Priority: {issue['priorityLabel']}"

            # Add labels if available
            if issue["labels"] and len(issue["labels"]) > 0:
                issue_text += f"\n  Labels: {', '.join(issue['labels'])}"

            # Add project if available
            if issue["project"]:
                issue_text += f"\n  Project: {issue['project']['name']}"

            # Add initiatives if available
            if issue["initiatives"] and len(issue["initiatives"]) > 0:
                initiative_names = [
                    initiative["name"] for initiative in issue["initiatives"]
                ]
                issue_text += f"\n  Initiatives: {', '.join(initiative_names)}"

            # Add description if available (truncated if too long)
            if issue["description"]:
                # Truncate description if it's too long
                description = issue["description"]
                DESCRIPTION_MAX_LENGTH = 200
                TRUNCATION_SUFFIX = "..."

                if len(description) > DESCRIPTION_MAX_LENGTH:
                    description = description[:DESCRIPTION_MAX_LENGTH - len(TRUNCATION_SUFFIX)] + TRUNCATION_SUFFIX
                issue_text += f"\n  Description: {description}"

            # Add URL
            issue_text += f"\n  URL: {issue['url']}"

            formatted_issues.append(issue_text)

        return "\n\n".join(formatted_issues)

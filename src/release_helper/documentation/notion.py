from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from notion_client import Client


if TYPE_CHECKING:
    from release_helper.issue_management.linear import IssueManagementLinear


class DocumentationNotion:
    def __init__(self, token: str, parent_page_id: str):
        self.client = self.get_client(token)
        self.parent_page_id = parent_page_id

    def get_client(self, token: str) -> Client:
        return Client(auth=token)

    def create_release_notes_page(
        self,
        release_title: str,
        release_body: str,
        release_url: str,
        issues: list[IssueManagementLinear.Issue],
        ai_generated_content: str,
    ) -> str:
        """Create a new page in Notion with the release notes.

        Args:
            release_title: The title of the release
            release_body: The body/description of the release
            release_url: The URL to the GitHub release
            issues: The list of Linear issues included in the release
            ai_generated_content: The AI-generated content for the release notes

        Returns:
            The URL of the created Notion page
        """
        logger.info(f"Creating Notion page for release: {release_title}")

        # Create the page
        page_properties = {
            "title": {
                "title": [{"text": {"content": f"Release Notes: {release_title}"}}]
            }
        }

        # Create the page content
        children = [
            # AI-generated content section
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Release Summary"}}
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": ai_generated_content}}
                    ]
                },
            },
            # GitHub release section
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "GitHub Release"}}
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "View on GitHub: "}},
                        {
                            "type": "text",
                            "text": {"content": release_title},
                            "href": release_url,
                        },
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": release_body}}]
                },
            },
            # Issues section
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Included Issues"}}
                    ]
                },
            },
        ]

        # Add each issue as a toggle block with details
        for issue in issues:
            # Create the toggle header with issue identifier and title
            toggle_block = {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"{issue.identifier}: {issue.title}"},
                            "href": issue.url,
                        }
                    ],
                    "children": [],
                },
            }

            # Add issue details as children of the toggle
            toggle_children = []

            # Add team info
            team_name = (
                issue.team.name if hasattr(issue.team, "name") else issue.team.key
            )
            toggle_children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"Team: {team_name}"}}
                        ]
                    },
                }
            )

            # Add assignee info
            assignee_name = issue.assignee.name if issue.assignee else "Unassigned"
            toggle_children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"Assignee: {assignee_name}"},
                            }
                        ]
                    },
                }
            )

            # Add priority if available
            if hasattr(issue, "priorityLabel") and issue.priorityLabel:
                toggle_children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Priority: {issue.priorityLabel}"
                                    },
                                }
                            ]
                        },
                    }
                )

            # Add labels if available
            if (
                hasattr(issue, "labels")
                and issue.labels
                and hasattr(issue.labels, "nodes")
            ):
                label_names = [label.name for label in issue.labels.nodes]
                if label_names:
                    toggle_children.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"Labels: {', '.join(label_names)}"
                                        },
                                    }
                                ]
                            },
                        }
                    )

            # Add project if available
            if hasattr(issue, "project") and issue.project:
                toggle_children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Project: {issue.project.name}"
                                    },
                                }
                            ]
                        },
                    }
                )

            # Add description if available
            if hasattr(issue, "description") and issue.description:
                toggle_children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "Description:"}}
                            ]
                        },
                    }
                )
                toggle_children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": issue.description}}
                            ]
                        },
                    }
                )

            # Add the children to the toggle
            toggle_block["toggle"]["children"] = toggle_children

            # Add the toggle block to the page
            children.append(toggle_block)

        # Create the page in Notion
        response = self.client.pages.create(
            parent={"page_id": self.parent_page_id},
            properties=page_properties,
            children=children,
        )

        logger.info(f"Created Notion page with ID: {response['id']}")
        return f"https://notion.so/{response['id'].replace('-', '')}"

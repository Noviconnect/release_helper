from dataclasses import dataclass


@dataclass
class ReleaseHelperError(Exception):
    message: str


class IssueError(ReleaseHelperError):
    def __init__(self, e: Exception):
        super().__init__(f"Error getting issue status: {e}")

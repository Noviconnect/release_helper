from dataclasses import dataclass


@dataclass
class ReleaseHelperError(Exception):
    message: str


@dataclass
class IssueError(ReleaseHelperError):
    linear_exception: Exception
    issue_id: str

    def __str__(self):
        return f"{self.message} Issue ID: {self.issue_id} Exception: {self.linear_exception}"

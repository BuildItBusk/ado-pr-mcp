"""Pydantic models for Azure DevOps pull request data."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PullRequestAuthor(BaseModel):
    """Author information for a pull request."""

    display_name: str = Field(..., description="Display name of the author")
    unique_name: str = Field(..., description="Unique name (typically email)")
    id: str = Field(..., description="Author ID")


class PullRequest(BaseModel):
    """Pull request data model."""

    pull_request_id: int = Field(..., description="Pull request ID")
    title: str = Field(..., description="Pull request title")
    description: Optional[str] = Field(None, description="Pull request description")
    status: str = Field(..., description="PR status (active, completed, abandoned)")
    created_date: datetime = Field(..., description="Creation date")
    created_by: PullRequestAuthor = Field(..., description="Author who created the PR")
    source_ref_name: str = Field(..., description="Source branch reference")
    target_ref_name: str = Field(..., description="Target branch reference")
    url: str = Field(..., description="Web URL to the pull request")
    repository_id: str = Field(..., description="Repository ID")


class PullRequestList(BaseModel):
    """List of pull requests with metadata."""

    pull_requests: List[PullRequest] = Field(
        default_factory=list, description="List of pull requests"
    )
    count: int = Field(..., description="Total count of pull requests")

    @classmethod
    def from_pull_requests(cls, prs: List[PullRequest]) -> "PullRequestList":
        """Create a PullRequestList from a list of PullRequests."""
        return cls(pull_requests=prs, count=len(prs))

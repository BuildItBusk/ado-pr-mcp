"""Azure DevOps REST API client using httpx."""

import base64
import logging
from typing import Optional
import httpx
from .models import PullRequest, PullRequestAuthor, PullRequestList

logger = logging.getLogger(__name__)


class AzureDevOpsClient:
    """Client for interacting with Azure DevOps REST API."""

    API_VERSION = "7.1"

    def __init__(self, organization: str, personal_access_token: str):
        """
        Initialize Azure DevOps client.

        Args:
            organization: Azure DevOps organization name
            personal_access_token: Personal Access Token for authentication
        """
        self.organization = organization
        self.base_url = f"https://dev.azure.com/{organization}"

        # Create Basic Auth header (username is empty, password is PAT)
        credentials = f":{personal_access_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"

        # Create httpx client with authentication
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_pull_requests(
        self,
        project: str,
        repository: str,
        status: str = "active",
    ) -> PullRequestList:
        """
        Get pull requests from an Azure DevOps repository.

        Args:
            project: Project name
            repository: Repository name or ID
            status: PR status filter (active, completed, abandoned, all)

        Returns:
            PullRequestList containing the pull requests

        Raises:
            httpx.HTTPStatusError: For HTTP errors (401, 404, etc.)
            httpx.ConnectError: For connection errors
            httpx.TimeoutException: For timeout errors
        """
        url = f"{self.base_url}/{project}/_apis/git/repositories/{repository}/pullrequests"

        params = {
            "api-version": self.API_VERSION,
        }

        # Only add status filter if not "all"
        if status != "all":
            params["searchCriteria.status"] = status

        logger.debug(f"Fetching PRs from {url} with params {params}")

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            pr_list = []

            for pr_data in data.get("value", []):
                # Extract created_by information
                created_by_data = pr_data.get("createdBy", {})
                created_by = PullRequestAuthor(
                    display_name=created_by_data.get("displayName", "Unknown"),
                    unique_name=created_by_data.get("uniqueName", ""),
                    id=created_by_data.get("id", ""),
                )

                # Create PullRequest model
                pr = PullRequest(
                    pull_request_id=pr_data["pullRequestId"],
                    title=pr_data["title"],
                    description=pr_data.get("description"),
                    status=pr_data["status"],
                    created_date=pr_data["creationDate"],
                    created_by=created_by,
                    source_ref_name=pr_data["sourceRefName"],
                    target_ref_name=pr_data["targetRefName"],
                    url=pr_data.get("url", ""),
                    repository_id=pr_data["repository"]["id"],
                )
                pr_list.append(pr)

            return PullRequestList.from_pull_requests(pr_list)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed - check your PAT token")
                raise ValueError(
                    "Authentication failed. Check AZURE_DEVOPS_PAT token and permissions"
                ) from e
            elif e.response.status_code == 404:
                logger.error(f"Project '{project}' or repository '{repository}' not found")
                raise ValueError(
                    f"Project '{project}' or repository '{repository}' not found"
                ) from e
            else:
                logger.error(f"HTTP error: {e}")
                raise

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.error(f"Network error: {e}")
            raise ValueError(f"Network error connecting to Azure DevOps: {e}") from e

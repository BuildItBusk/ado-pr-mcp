"""MCP resources for Azure DevOps pull requests."""

import logging
from typing import Optional
from .azure_client import AzureDevOpsClient
from .git_detector import detect_current_repo
from .config import get_settings

logger = logging.getLogger(__name__)

# Global Azure client (lazy initialization)
_ado_client: Optional[AzureDevOpsClient] = None


async def get_ado_client() -> AzureDevOpsClient:
    """Get or create the Azure DevOps client instance."""
    global _ado_client

    if _ado_client is None:
        settings = get_settings()

        # Try to detect current repo for default organization
        repo_info = detect_current_repo()
        org = repo_info.organization if repo_info else settings.ado_organization

        if not org:
            raise ValueError(
                "No organization found. Set ADO_ORGANIZATION environment variable "
                "or run from an Azure DevOps git repository"
            )

        logger.info(f"Initializing Azure DevOps client for organization: {org}")
        _ado_client = AzureDevOpsClient(org, settings.azure_devops_pat)

    return _ado_client


async def list_pull_requests_resource(
    organization: str,
    project: str,
    repository: str,
    status: str = "active",
) -> str:
    """
    List pull requests from an Azure DevOps repository.

    Args:
        organization: Azure DevOps organization name
        project: Project name
        repository: Repository name or ID
        status: PR status filter (active, completed, abandoned, all)

    Returns:
        JSON string containing pull request list
    """
    try:
        client = await get_ado_client()
        result = await client.get_pull_requests(project, repository, status)
        return result.model_dump_json(indent=2)
    except Exception as e:
        logger.error(f"Error listing PRs: {e}", exc_info=True)
        raise


async def list_current_pull_requests_resource(status: str = "active") -> str:
    """
    List pull requests from the current repository (auto-detected from git).

    Args:
        status: PR status filter (active, completed, abandoned, all)

    Returns:
        JSON string containing pull request list or error message
    """
    try:
        repo_info = detect_current_repo()

        if not repo_info:
            error_response = {
                "error": "Not in an Azure DevOps git repository",
                "suggestion": "Use explicit organization/project/repository parameters or run from an Azure DevOps git repository",
            }
            import json
            return json.dumps(error_response, indent=2)

        logger.info(
            f"Detected repo: {repo_info.organization}/{repo_info.project}/{repo_info.repository}"
        )

        client = await get_ado_client()
        result = await client.get_pull_requests(
            repo_info.project,
            repo_info.repository,
            status,
        )
        return result.model_dump_json(indent=2)

    except Exception as e:
        logger.error(f"Error listing current repo PRs: {e}", exc_info=True)
        raise

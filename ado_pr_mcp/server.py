"""MCP server for Azure DevOps pull requests."""

import logging
import sys
from fastmcp import FastMCP
from .config import get_settings
from .resources import list_pull_requests_resource, list_current_pull_requests_resource

# Configure logging to stderr (critical for stdio transport)
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.mcp_log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("ado-pr-mcp")


@mcp.resource("ado://pull-requests/{organization}/{project}/{repository}")
async def list_pull_requests(
    uri: str,
    organization: str,
    project: str,
    repository: str,
    status: str = "active",
) -> str:
    """
    List pull requests from an Azure DevOps repository.

    Args:
        uri: Resource URI
        organization: Azure DevOps organization name
        project: Project name
        repository: Repository name or ID
        status: PR status filter (active, completed, abandoned, all)

    Returns:
        JSON string containing pull request list
    """
    logger.info(
        f"Fetching PRs for {organization}/{project}/{repository} with status={status}"
    )
    return await list_pull_requests_resource(organization, project, repository, status)


@mcp.resource("ado://pull-requests/current")
async def list_current_pull_requests(
    uri: str,
    status: str = "active",
) -> str:
    """
    List pull requests from the current repository (auto-detected from git).

    Args:
        uri: Resource URI
        status: PR status filter (active, completed, abandoned, all)

    Returns:
        JSON string containing pull request list
    """
    logger.info(f"Fetching PRs for current repository with status={status}")
    return await list_current_pull_requests_resource(status)


def run_server():
    """Run the MCP server."""
    logger.info("Starting ADO PR MCP Server")
    logger.info(f"Transport: {settings.mcp_transport}")
    logger.info(f"Log level: {settings.mcp_log_level}")

    try:
        if settings.mcp_transport == "stdio":
            mcp.run(transport="stdio")
        else:
            # HTTP transport
            mcp.run(transport="sse", port=8000)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise

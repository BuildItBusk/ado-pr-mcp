"""Tests for Azure DevOps client."""

import pytest
import httpx
from ado_pr_mcp.models import PullRequestList
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_pull_requests_success(ado_client, mock_pr_response):
    """Test successful pull request retrieval."""
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_pr_response
    mock_response.raise_for_status = MagicMock()

    # Patch the client.get method
    ado_client.client.get = AsyncMock(return_value=mock_response)

    # Call the method
    result = await ado_client.get_pull_requests("testproj", "testrepo", "active")

    # Assertions
    assert isinstance(result, PullRequestList)
    assert result.count == 1
    assert len(result.pull_requests) == 1

    pr = result.pull_requests[0]
    assert pr.pull_request_id == 123
    assert pr.title == "Test PR"
    assert pr.status == "active"
    assert pr.created_by.display_name == "John Doe"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_pull_requests_empty(ado_client):
    """Test pull request retrieval with no results."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": []}
    mock_response.raise_for_status = MagicMock()

    ado_client.client.get = AsyncMock(return_value=mock_response)

    result = await ado_client.get_pull_requests("testproj", "testrepo", "active")

    assert isinstance(result, PullRequestList)
    assert result.count == 0
    assert len(result.pull_requests) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_pull_requests_auth_failure(ado_client):
    """Test authentication failure handling."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=mock_response
    )

    ado_client.client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError, match="Authentication failed"):
        await ado_client.get_pull_requests("testproj", "testrepo", "active")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_pull_requests_not_found(ado_client):
    """Test handling of non-existent project or repository."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    ado_client.client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError, match="not found"):
        await ado_client.get_pull_requests("badproj", "badrepo", "active")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_client_close(ado_client):
    """Test client cleanup."""
    await ado_client.close()
    # Client should be closed without error
    assert True

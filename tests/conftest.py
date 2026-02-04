"""Shared pytest fixtures for all tests."""

import os
import pytest
import pytest_asyncio
from unittest.mock import MagicMock
from ado_pr_mcp.azure_client import AzureDevOpsClient


# Unit Test Fixtures


@pytest.fixture
def mock_pat():
    """Mock PAT token for testing."""
    return "fake_pat_token_for_testing"


@pytest.fixture
def ado_client(mock_pat):
    """Create a test Azure DevOps client with mock PAT."""
    return AzureDevOpsClient("testorg", mock_pat)


@pytest.fixture
def mock_pr_author():
    """Create a mock PR author."""
    return {
        "displayName": "John Doe",
        "uniqueName": "john@example.com",
        "id": "user-id-123",
    }


@pytest.fixture
def mock_pr_data(mock_pr_author):
    """Create mock PR data matching Azure DevOps API format."""
    return {
        "pullRequestId": 123,
        "title": "Test PR",
        "description": "Test description",
        "status": "active",
        "creationDate": "2024-01-01T00:00:00Z",
        "createdBy": mock_pr_author,
        "sourceRefName": "refs/heads/feature",
        "targetRefName": "refs/heads/main",
        "url": "https://dev.azure.com/testorg/testproj/_git/testrepo/pullrequest/123",
        "repository": {"id": "repo-id-456"},
    }


@pytest.fixture
def mock_pr_response(mock_pr_data):
    """Mock Azure DevOps PR API response."""
    return {"value": [mock_pr_data]}


@pytest.fixture
def mock_empty_response():
    """Mock empty PR response."""
    return {"value": []}


# Integration Test Fixtures


@pytest.fixture(scope="session")
def integration_config():
    """
    Configuration for integration tests.

    Skips tests if required environment variables are not set.
    """
    pat = os.getenv("AZURE_DEVOPS_PAT")
    org = os.getenv("ADO_TEST_ORGANIZATION")
    project = os.getenv("ADO_TEST_PROJECT")
    repo = os.getenv("ADO_TEST_REPOSITORY")

    if not all([pat, org, project, repo]):
        pytest.skip(
            "Integration tests require environment variables: "
            "AZURE_DEVOPS_PAT, ADO_TEST_ORGANIZATION, "
            "ADO_TEST_PROJECT, ADO_TEST_REPOSITORY"
        )

    return {
        "pat": pat,
        "organization": org,
        "project": project,
        "repository": repo,
    }


@pytest_asyncio.fixture
async def live_ado_client(integration_config):
    """
    Create a real Azure DevOps client for integration tests.

    Automatically closes the client after tests complete.
    """
    client = AzureDevOpsClient(
        integration_config["organization"],
        integration_config["pat"]
    )
    yield client
    await client.close()

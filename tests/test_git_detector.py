"""Tests for git repository detection."""

import subprocess
from unittest.mock import MagicMock, patch
import pytest
from ado_pr_mcp.git_detector import (
    get_git_remote_url,
    parse_azure_devops_url,
    detect_current_repo,
    RepoInfo,
)


def test_parse_modern_azure_devops_url():
    """Test parsing modern dev.azure.com URL format."""
    url = "https://dev.azure.com/myorg/MyProject/_git/MyRepo"
    result = parse_azure_devops_url(url)

    assert result is not None
    assert result.organization == "myorg"
    assert result.project == "MyProject"
    assert result.repository == "MyRepo"


def test_parse_legacy_visualstudio_url():
    """Test parsing legacy visualstudio.com URL format."""
    url = "https://myorg.visualstudio.com/MyProject/_git/MyRepo"
    result = parse_azure_devops_url(url)

    assert result is not None
    assert result.organization == "myorg"
    assert result.project == "MyProject"
    assert result.repository == "MyRepo"


def test_parse_non_azure_url():
    """Test that non-Azure DevOps URLs return None."""
    url = "https://github.com/user/repo.git"
    result = parse_azure_devops_url(url)

    assert result is None


def test_parse_invalid_url():
    """Test that invalid URLs return None."""
    url = "not-a-valid-url"
    result = parse_azure_devops_url(url)

    assert result is None


@patch("subprocess.run")
def test_get_git_remote_url_success(mock_run):
    """Test successful git remote URL retrieval."""
    mock_run.return_value = MagicMock(
        stdout="https://dev.azure.com/org/proj/_git/repo\n",
        returncode=0,
    )

    result = get_git_remote_url()

    assert result == "https://dev.azure.com/org/proj/_git/repo"
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_get_git_remote_url_not_in_repo(mock_run):
    """Test git remote URL when not in a repository."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "git")

    result = get_git_remote_url()

    assert result is None


@patch("subprocess.run")
def test_get_git_remote_url_timeout(mock_run):
    """Test git remote URL when command times out."""
    mock_run.side_effect = subprocess.TimeoutExpired("git", 5)

    result = get_git_remote_url()

    assert result is None


@patch("ado_pr_mcp.git_detector.get_git_remote_url")
def test_detect_current_repo_success(mock_get_url):
    """Test successful current repository detection."""
    mock_get_url.return_value = "https://dev.azure.com/org/proj/_git/repo"

    result = detect_current_repo()

    assert result is not None
    assert result.organization == "org"
    assert result.project == "proj"
    assert result.repository == "repo"


@patch("ado_pr_mcp.git_detector.get_git_remote_url")
def test_detect_current_repo_no_git(mock_get_url):
    """Test repository detection when not in a git repository."""
    mock_get_url.return_value = None

    result = detect_current_repo()

    assert result is None


@patch("ado_pr_mcp.git_detector.get_git_remote_url")
def test_detect_current_repo_non_azure(mock_get_url):
    """Test repository detection with non-Azure DevOps git remote."""
    mock_get_url.return_value = "https://github.com/user/repo.git"

    result = detect_current_repo()

    assert result is None

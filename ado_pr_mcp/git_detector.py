"""Git repository detection for Azure DevOps."""

import re
import subprocess
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class RepoInfo:
    """Azure DevOps repository information."""

    organization: str
    project: str
    repository: str


def get_git_remote_url() -> Optional[str]:
    """
    Get the git remote URL from the current directory.

    Returns:
        The remote URL or None if not in a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def parse_azure_devops_url(git_url: str) -> Optional[RepoInfo]:
    """
    Parse an Azure DevOps git URL to extract organization, project, and repository.

    Supports both modern and legacy URL formats:
    - Modern: https://dev.azure.com/{org}/{project}/_git/{repo}
    - Legacy: https://{org}.visualstudio.com/{project}/_git/{repo}

    Args:
        git_url: Git remote URL to parse

    Returns:
        RepoInfo with extracted information or None if not a valid Azure DevOps URL
    """
    parsed = urlparse(git_url)

    # Handle modern dev.azure.com format
    if "dev.azure.com" in parsed.netloc:
        # Pattern: /org/project/_git/repo
        pattern = r"/([^/]+)/([^/]+)/_git/([^/]+)"
        match = re.search(pattern, parsed.path)
        if match:
            return RepoInfo(
                organization=match.group(1),
                project=match.group(2),
                repository=match.group(3),
            )

    # Handle legacy visualstudio.com format
    elif "visualstudio.com" in parsed.netloc:
        # Extract org from subdomain
        org_match = re.match(r"^([^.]+)\.visualstudio\.com", parsed.netloc)
        if org_match:
            org = org_match.group(1)
            # Pattern: /project/_git/repo
            pattern = r"/([^/]+)/_git/([^/]+)"
            match = re.search(pattern, parsed.path)
            if match:
                return RepoInfo(
                    organization=org,
                    project=match.group(1),
                    repository=match.group(2),
                )

    return None


def detect_current_repo() -> Optional[RepoInfo]:
    """
    Detect the current Azure DevOps repository from git configuration.

    Returns:
        RepoInfo if in an Azure DevOps git repository, None otherwise
    """
    url = get_git_remote_url()
    if url:
        return parse_azure_devops_url(url)
    return None

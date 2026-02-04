# ADO PR MCP - Project Context

## Project Overview
An MCP (Model Context Protocol) server for Azure DevOps Pull Requests. Provides read access to PRs via MCP resources with planned write operations via MCP tools.

## Project Structure
```
ado-pr-mcp/
├── ado_pr_mcp/              # Main package
│   ├── __init__.py
│   ├── azure_client.py      # Azure DevOps HTTP client (httpx)
│   ├── config.py            # Pydantic settings
│   ├── git_detector.py      # Git remote URL parsing
│   ├── models.py            # Pydantic data models
│   ├── resources.py         # MCP resource implementations
│   ├── server.py            # MCP server setup (FastMCP)
│   └── tools.py             # Future tools (Phase 2)
├── tests/                   # Unit tests
│   ├── test_azure_client.py
│   └── test_git_detector.py
├── main.py                  # Entry point
├── pyproject.toml           # Dependencies (strict pinning)
├── .env.example             # Environment template
└── README.md                # Documentation
```

## Technology Stack
- **Language**: Python 3.14+
- **Package Manager**: uv
- **MCP Framework**: FastMCP 2.14.5
- **HTTP Client**: httpx 0.28.1 (direct REST API calls)
- **Validation**: Pydantic 2.12.5
- **Testing**: pytest, pytest-asyncio

## Dependencies Philosophy
- **Strict version pinning** for all dependencies
- Deliberate updates after reviewing changelogs
- Using `httpx` directly instead of `azure-devops` SDK for lighter footprint

### Dependency Management
```bash
# Check for outdated packages
uv pip list --outdated

# Update specific package after reviewing changelog
# 1. Review changelog at PyPI or GitHub
# 2. Update version in pyproject.toml
# 3. Run: uv sync --extra dev
# 4. Run tests: uv run pytest tests/
```

## Current Status
✅ **Phase 1 Complete:**
- MCP server with FastMCP
- Two MCP resources implemented:
  - `ado://pull-requests/{org}/{project}/{repo}` - Explicit
  - `ado://pull-requests/current` - Auto-detect from git
- Azure DevOps REST API client with httpx
- Git repository auto-detection (modern & legacy formats)
- Configuration management with Pydantic
- Unit tests (15 tests, all passing)
- Comprehensive documentation

## Configuration
Requires `AZURE_DEVOPS_PAT` environment variable. Optional org/project/repo defaults. See `.env.example`.

## Usage
```bash
# Install dependencies
uv sync --extra dev

# Run server
python main.py

# Run tests
uv run pytest tests/
```

## Next Steps (Phase 2)
- Implement MCP tools for write operations:
  - Comment on PRs
  - Create PRs
  - Update PRs
  - Approve & complete PRs
- Add pagination for large result sets
- Advanced filtering options

## Git Commit Guidelines
**Format**: One title line + 5-10 concise bullet points

```
Title summarizing the change

- Specific change with technical value
- Another meaningful change
- Key upgrade or fix with reason
- Configuration or structural change
- Impact or benefit to developers
```

**Rules**:
- Focus on changes that provide value to future developers
- Include technical reasons for upgrades (e.g., "fixes deprecation warnings")
- Omit meta-information like "Made by Claude" or "AI-assisted"
- Keep bullets factual and concise

## Architecture Notes
- Logs to stderr (critical for stdio transport)
- Base64 PAT authentication
- Pydantic for type safety throughout
- Async/await for all HTTP calls
- Error handling for auth, 404, network issues

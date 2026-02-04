# Azure DevOps PR MCP Server

An MCP (Model Context Protocol) server for Azure DevOps pull requests. This server provides read access to pull requests via MCP resources, with future support planned for write operations via MCP tools.

## Features

### Phase 1 (Current)
- **List Pull Requests**: Read pull requests from Azure DevOps repositories
- **Auto-detection**: Automatically detect repository info from git configuration
- **Status Filtering**: Filter PRs by status (active, completed, abandoned, all)
- **Direct HTTP Calls**: Lightweight implementation using httpx instead of heavy SDK

### Phase 2 (Planned)
- Comment on pull requests
- Create new pull requests
- Update PR details
- Approve and complete pull requests

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

**Required:**
- `AZURE_DEVOPS_PAT` - Your Personal Access Token (needs "Code (Read)" scope)

**Optional:**
- `ADO_ORGANIZATION` - Default organization (used when not in a git repo)
- `ADO_PROJECT` - Default project
- `ADO_REPOSITORY` - Default repository
- `MCP_TRANSPORT` - Transport type: "stdio" (default) or "http"
- `MCP_LOG_LEVEL` - Log level: "INFO" (default), "DEBUG", "WARNING", "ERROR"

### Creating a Personal Access Token (PAT)

1. Go to `https://dev.azure.com/{your-organization}/_usersSettings/tokens`
2. Click "New Token"
3. Give it a name and set expiration
4. Under "Scopes", select:
   - **Code (Read)** for Phase 1 (reading PRs)
   - **Code (Read & Write)** for Phase 2 (when implementing write operations)
5. Click "Create" and copy the token
6. Add it to your `.env` file as `AZURE_DEVOPS_PAT`

## Usage

### Running the Server

```bash
python main.py
```

The server will start with stdio transport by default, suitable for integration with MCP clients.

### MCP Resources

The server exposes two MCP resources:

#### 1. Explicit Repository

Query a specific repository:

```
ado://pull-requests/{organization}/{project}/{repository}?status=active
```

Example:
```
ado://pull-requests/myorg/MyProject/MyRepo?status=active
```

#### 2. Current Repository (Auto-detect)

Query the current git repository (auto-detected):

```
ado://pull-requests/current?status=active
```

This automatically detects the Azure DevOps organization, project, and repository from your git remote URL.

### Status Filters

- `active` - Open pull requests (default)
- `completed` - Merged/completed pull requests
- `abandoned` - Abandoned pull requests
- `all` - All pull requests regardless of status

## Development

### Running Tests

```bash
uv run pytest tests/
```

With coverage:

```bash
uv run pytest --cov=ado_pr_mcp tests/
```

### Project Structure

```
ado-pr-mcp/
├── ado_pr_mcp/          # Main package
│   ├── azure_client.py  # Azure DevOps HTTP client
│   ├── config.py        # Configuration management
│   ├── git_detector.py  # Git repository detection
│   ├── models.py        # Pydantic data models
│   ├── resources.py     # MCP resource implementations
│   ├── server.py        # MCP server setup
│   └── tools.py         # Future tools (Phase 2)
├── tests/               # Unit tests
├── main.py              # Entry point
└── pyproject.toml       # Dependencies
```

## Architecture

### Dependency Philosophy

This project uses **strict version pinning** for all dependencies:
- Ensures reproducible builds
- Prevents unexpected breaking changes
- Dependencies updated deliberately after reviewing changelogs

### Why httpx instead of azure-devops SDK?

- **Lighter**: Minimal dependency footprint
- **Transparent**: Full visibility into HTTP requests
- **Flexible**: Easy to extend and customize
- **Debuggable**: Clear error messages and request/response inspection

## Troubleshooting

### "Authentication failed"
- Verify your `AZURE_DEVOPS_PAT` is correct
- Ensure the PAT has "Code (Read)" scope
- Check the PAT hasn't expired

### "Project or repository not found"
- Verify the organization, project, and repository names are correct
- Check you have access to the repository
- Ensure the repository exists in Azure DevOps

### "Not in an Azure DevOps git repository"
- This error occurs when using `ado://pull-requests/current` outside a git repo
- Either run from within an Azure DevOps git repository
- Or use the explicit URI format with organization/project/repository parameters
- Or set `ADO_ORGANIZATION`, `ADO_PROJECT`, `ADO_REPOSITORY` environment variables

### Network errors
- Check your internet connection
- Verify Azure DevOps is accessible: `https://dev.azure.com`
- Check for proxy or firewall issues

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows existing style
- New features include tests
- Documentation is updated

## License

See LICENSE file for details.

## Roadmap

- [x] Phase 1: Read pull requests via MCP resources
- [ ] Phase 2: Write operations via MCP tools
  - [ ] Comment on PRs
  - [ ] Create PRs
  - [ ] Update PRs
  - [ ] Approve PRs
  - [ ] Complete/merge PRs
- [ ] Advanced filtering (author, labels, dates)
- [ ] Pagination for large result sets
- [ ] Work item integration

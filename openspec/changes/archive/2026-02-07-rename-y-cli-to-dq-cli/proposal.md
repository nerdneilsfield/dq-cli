# Rename y-cli to dq-cli

## Why

The project has been renamed from y-cli to dq-cli to better reflect its identity and ownership. All references to "y-cli" in code, configuration, documentation, and metadata need to be updated to "dq-cli" to ensure consistency across the codebase and user experience.

## What Changes

This change updates all occurrences of "y-cli" to "dq-cli" throughout the project, including:

- **Package metadata**: PyPI package name, script entry points
- **Configuration paths**: Application data directories, config file locations
- **Documentation**: README, docs, codemaps, memory-bank files
- **Source code**: App name variables, user-facing strings, User-Agent headers
- **CI/CD**: GitHub workflows, publish scripts
- **Project context**: OpenSpec project.md and related files

## Capabilities

### Modified Capabilities
- `project-identity`: All references to the project name are updated from y-cli to dq-cli
- `configuration-management`: Config paths now use "dq-cli" directory names (e.g., `~/Library/Application Support/dq-cli`)
- `cli-entry-point`: Command-line script renamed from `y-cli` to `dq-cli`

## Impact

- `pyproject.toml`: Package name and script entry point
- `src/config.py`: app_name variable (2 occurrences)
- `src/cli/__init__.py`: CLI help text
- `src/cli/commands/init.py`: Initialization prompts
- `src/cli/commands/daemon/utils.py`: Daemon socket paths
- `src/daemon_client/main.py`: Client socket paths
- `src/mcp_daemon/main.py`: Daemon log and socket paths
- `src/prompt/mcp.py`: Prompt text
- `src/chat/provider/openai_format_provider.py`: User-Agent header
- `README.md`: All documentation and examples (10 occurrences)
- `docs/*.md`: MCP_DAEMON.md, CLOUDFLARE_D1.md, PROMPT_CONFIGURATION.md (31 total)
- `codemaps/codemap.md`: Code map documentation (7 occurrences)
- `openspec/project.md`: Project context (11 occurrences)
- `memory-bank/*.md`: Context files (6 occurrences)
- `.github/workflows/publish.yml`: CI/CD pipeline
- `LICENSE`: Project name reference
- `.clinerules`: Configuration rules

**Total**: 25 files, 87 occurrences

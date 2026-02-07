# Implementation Tasks

## 1. Update Package Metadata

- [x] 1.1 Update package name in pyproject.toml: "y-cli" → "dq-cli"
- [x] 1.2 Update script entry point in pyproject.toml: "y-cli" → "dq-cli"

## 2. Update Core Configuration

- [x] 2.1 Update app_name in src/config.py get_default_config(): "y-cli" → "dq-cli"
- [x] 2.2 Update app_name in src/config.py load_config(): "y-cli" → "dq-cli"

## 3. Update Source Code Files

- [x] 3.1 Update CLI description in src/cli/__init__.py
- [x] 3.2 Update initialization prompts in src/cli/commands/init.py
- [x] 3.3 Update daemon paths in src/cli/commands/daemon/utils.py
- [x] 3.4 Update daemon client paths in src/daemon_client/main.py
- [x] 3.5 Update daemon server paths in src/mcp_daemon/main.py
- [x] 3.6 Update prompt text in src/prompt/mcp.py
- [x] 3.7 Update User-Agent in src/chat/provider/openai_format_provider.py

## 4. Update Documentation

- [x] 4.1 Update README.md (10 occurrences)
- [x] 4.2 Update docs/MCP_DAEMON.md
- [x] 4.3 Update docs/CLOUDFLARE_D1.md
- [x] 4.4 Update docs/PROMPT_CONFIGURATION.md
- [x] 4.5 Update codemaps/codemap.md (7 occurrences)

## 5. Update Context Files

- [x] 5.1 Update openspec/project.md (11 occurrences)
- [x] 5.2 Update memory-bank/productContext.md
- [x] 5.3 Update memory-bank/progress.md
- [x] 5.4 Update memory-bank/projectbrief.md
- [x] 5.5 Update memory-bank/systemPatterns.md
- [x] 5.6 Update memory-bank/techContext.md
- [x] 5.7 Update memory-bank/activeContext.md

## 6. Update CI/CD and Metadata

- [x] 6.1 Update .github/workflows/publish.yml
- [x] 6.2 Update LICENSE
- [x] 6.3 Update .clinerules

## 7. Verify

- [x] 7.1 Verify no "y-cli" references remain (grep search)
- [x] 7.2 Test that `dq-cli` command entry point works
- [x] 7.3 Verify config paths are correct in code

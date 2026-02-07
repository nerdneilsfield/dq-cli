# Project Identity Specification

## ADDED Requirements

### Requirement: All project references SHALL use dq-cli naming

All references to the project name throughout the codebase, documentation, and configuration SHALL consistently use "dq-cli" instead of "y-cli".

#### Scenario: Package metadata uses dq-cli

- **WHEN** the package is defined in pyproject.toml
- **THEN** the package name is "dq-cli"
- **AND** the script entry point is "dq-cli"

#### Scenario: Configuration paths use dq-cli directories

- **WHEN** the application creates or accesses configuration directories
- **THEN** the directory names include "dq-cli" (e.g., `~/Library/Application Support/dq-cli`)
- **AND** all platform-specific paths (macOS, Linux) use "dq-cli"

#### Scenario: Source code uses dq-cli app name

- **WHEN** source code defines or references the application name
- **THEN** the app_name variable is "dq-cli"
- **AND** all hardcoded string references use "dq-cli"

#### Scenario: Documentation references dq-cli

- **WHEN** documentation describes the project or provides usage examples
- **THEN** all project name references are "dq-cli"
- **AND** all command examples use `dq-cli` command
- **AND** all installation instructions reference "dq-cli"

#### Scenario: User-facing strings use dq-cli

- **WHEN** the CLI displays help text, prompts, or messages to users
- **THEN** all visible strings reference "dq-cli"
- **AND** the User-Agent header in HTTP requests uses "dq-cli"

#### Scenario: CI/CD pipeline uses dq-cli

- **WHEN** GitHub workflows build or publish the package
- **THEN** the workflow references "dq-cli"
- **AND** published artifacts use "dq-cli" naming

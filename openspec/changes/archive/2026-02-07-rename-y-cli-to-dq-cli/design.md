# Design: Rename y-cli to dq-cli

## Context

The project was originally named "y-cli" but needs to be renamed to "dq-cli". This is a straightforward search-and-replace operation across 25 files with 87 total occurrences.

## Goals / Non-Goals

**Goals:**
- Update all references from "y-cli" to "dq-cli" consistently
- Maintain backward compatibility where possible (existing user data paths)
- Ensure documentation and code stay in sync

**Non-Goals:**
- Migrating existing user data to new paths (users can manually migrate if desired)
- Creating aliases or symlinks for backward compatibility
- Updating external references (PyPI, GitHub, etc.) - those are separate deployment steps

## Decisions

### Decision 1: Direct string replacement approach

**Approach**: Use direct find-and-replace for all occurrences of "y-cli" → "dq-cli"

**Rationale**:
- Simple and low-risk
- Easy to verify completeness
- No complex logic or migration code needed

**Trade-offs**:
- Existing users will see config paths change (new location)
- Old installations won't automatically migrate
- Acceptable because this is a development project and users can manually update

### Decision 2: Update all file categories in one change

**Categories to update**:
1. Core configuration (pyproject.toml, config.py)
2. Source code (all .py files with references)
3. Documentation (README, docs/*, codemaps/*, memory-bank/*)
4. OpenSpec project context (openspec/project.md)
5. CI/CD (.github/workflows/*)
6. Metadata (LICENSE, .clinerules)

**Rationale**:
- Ensures atomicity - everything changes together
- Prevents inconsistent state where some files use old name
- Single commit makes rollback easier if needed

### Decision 3: No data migration logic

We will NOT add code to automatically migrate user data from old paths to new paths.

**Rationale**:
- Adds complexity for minimal benefit
- Users can manually copy data if needed
- Most users are likely developers who can handle migration
- Keeps this change purely about naming, not migration

### Decision 4: File-by-file replacement

Process files in logical order:
1. Package metadata (pyproject.toml)
2. Core config (src/config.py)
3. Source code (src/**/*.py)
4. Documentation (README, docs, codemaps, memory-bank)
5. OpenSpec context
6. CI/CD and other files

**Rationale**: Start with most critical files first, then move to documentation.

## Implementation Notes

- Use case-sensitive replacement: "y-cli" → "dq-cli" (not "Y-CLI" or other variants)
- Verify no unintended replacements (e.g., in URLs that shouldn't change)
- Test that `dq-cli` command works after changes
- Update openspec/project.md to reflect the new project name

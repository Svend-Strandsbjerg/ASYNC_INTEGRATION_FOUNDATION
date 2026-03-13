# Contributing Guide

Thanks for contributing to `ASYNC_INTEGRATION_FOUNDATION`.

This guide applies to both human contributors and AI agents.

## Contribution model

- All work is done in branches.
- All changes are submitted through pull requests.
- Direct commits to `main` are not allowed.

## Project-specific expectations

Because this repository is a reusable async framework foundation:

- Keep core modules business-neutral.
- Prefer interface-first changes before concrete runtime complexity.
- Add or update documentation with every architectural or behavioral change.
- Include tests for state transitions, dispatch behavior, and retry semantics when relevant.

## Getting started

1. Read `README.md`, `ARCHITECTURE.md`, and `AGENTS.md`.
2. Review framework docs in `docs/framework/`.
3. Confirm task scope and acceptance criteria.
4. Create a branch from `main`.
5. Make focused, reviewable changes.
6. Run relevant checks/tests.
7. Open a PR using `.github/pull_request_template.md`.

## What good contributions look like

- Clear problem statement and scope boundaries
- Minimal, maintainable implementation
- Tests that validate behavior and prevent regressions
- Documentation updates when process/behavior/structure changes
- Transparent assumptions and risk notes

## Pull request requirements

PRs should include:

- Summary of changes
- Problem being solved
- Testing evidence
- Documentation updates
- Risks, assumptions, and follow-up recommendations

Use the checklist in the PR template before requesting review.

## AI-assisted contribution expectations

When using AI agents/tools:

- Review generated output before submission.
- Ensure generated code/docs follow repository standards.
- Validate claims (tests run, behavior, and side effects).
- Keep AI-generated changes scoped; avoid large unreviewable diffs.

## Review and merge

- At least one human reviewer approval is required.
- Required CI checks must pass.
- Address reviewer feedback with follow-up commits on the same branch.
- Merge only after approval and green checks.

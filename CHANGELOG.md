# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.8] - 2026-10-30

### Changed
- Require `scion-sdk>=0.6.4,<0.7.0`; `uv.lock` relocked.

## [2.3.6] - 2026-10-27

### Added
- Packaged development skill for the `PIPE-CONNSPEC-R122.4` delivery contract.

## [2.3.5] - 2026-10-24

### Changed
- Central connector migration: requires `agent-connector-sdk>=0.5.4`; server bootstrap, version, containers, ontology artifacts, security scaffold and pre-commit config are provided centrally.

## [Unreleased]

### Added
- `concept(id)` pytest marker registration and `@pytest.mark.concept` traceability
  markers (plus `CONCEPT:FRSS-*` docstrings) on all test functions.
- README Table of Contents, Key Features, Available MCP Tools table, Usage examples,
  expanded Installation, and a Documentation section linking the `docs/` material.

## [0.1.0] - 2026-06-18

### Added
- Initial release.
- Modular subfolders for API wrappers (`api/`) and action-routed MCP tools (`mcp/`).
- Material-theme mkdocs documentation site (7 standard pages).
- Full pre-commit quality gate and flat `tests/` structure.

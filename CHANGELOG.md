# Changelog

All notable changes to this project are documented here. Indicator IDs (`AMS-*`) are stable;
see [SPEC.md](SPEC.md) for the versioning policy.

## 0.5.1 — 2026-07-12

**Packaging fix (important if you installed 0.5.0 via pip):** stale `build/` and `*.egg-info/`
directories were committed to the repository, and setuptools packaged the outdated code inside
them — a `pip install` of "0.5.0" was missing the `verdict` field and other 0.5.0 changes.
Removed the stale artifacts and ignored them permanently. Reinstall with
`pip install --force-reinstall --no-cache-dir "git+https://github.com/Echolonius/agent-market-signals"`.

Also new: the project site with an in-browser detector demo — https://echolonius.github.io/agent-market-signals/

## 0.5.0
- Add an at-a-glance `verdict` to scan reports: `high_risk` / `caution` / `clear`. Deliberately
  categorical, not a false-precise 0–100 score.
- Continuous integration (GitHub Actions) running the suite on Python 3.9–3.12.
- Project logo and documented changelog.

## 0.4.0
- MCP server: expose the detectors as tools an agent can call at decision time
  (`scan_listings`, `check_listing`, `list_indicators`, `make_observation`).
- `mcp` kept as an optional extra so the core stays dependency-free.
- `Listing.from_dict` / `parse_created_at` helpers shared by the CLI and server.

## 0.3.0
- Privacy-preserving, opt-in contribution primitive (`to_observation`) with a k-anonymity floor
  and no identifiers — the safe core of the improvement "flywheel" (see FLYWHEEL.md).

## 0.2.0
- Open specification (SPEC.md) with stable indicator IDs `AMS-001`–`AMS-005`.
- Accuracy: infer `views_tracked` platform-wide and suppress view-based indicators when a platform
  does not expose views (removes a class of false positives).
- Data-coverage reporting in scan output.
- Installable from GitHub via `pyproject.toml`.

## 0.1.0
- Initial release: five dependency-free detectors, `scan()` orchestration, CLI, tests, and a
  synthetic example dataset.

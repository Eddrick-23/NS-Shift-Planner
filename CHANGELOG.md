# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
---
## [2.0.2-beta] - 2026-08-01
### Added
- bug fix for backend "prune_db" method. When a session is pruned, its record in `app.state.cache` is also removed.
- bug fix for CustomLRUCache in lru_cache.py `expire_at` in `sync to firebase` set to follow `config.DATA_EXPIRY_LENGTH`. Previously set to `1`.
- bug fix for backend "GridManager.swap_hours" method. Also updates total hour count for that specific name after swapping.
- bug fix for frontend, Swap names name selection is empty when Night Duty Grid is in compressed mode
- Unit tests for api background job(cache scanning and session pruning) behaviour.

### Changed
- Removed ThreadSafeSet class since we do not cache all ids. Use db as source of truth.
- Removed GridManager.swap_hours, use GridManager.update_hours instead for swap-names endpoint
---
## [2.0.1-beta] - 2025-08-04
### Added
- "/" endpoint to api which returns api name, version, and status.
- Tab name "NS Planner" instead of "Vite + Vue"
### Changed
- Docker image for backend changed to python-slim from distroless due to instability in pulling distroless image in builds.
- backend bug fix, reset scan cache counter after each iteration.
- backend changed login endpoint behaviour. On valid id, data is restored from databased and loaded to cache.
- fix `<label for=""> `usage in LocationRadio.vue and ShiftSizeRadio.vue to match RadioButton "inputId".
## [2.0.0-beta] - 2025-08-04

### Changed
- ported frontend over to Vue-Js
- Replace sessionId management to http cookies stored in browser

## [1.0.1-beta] - 2025-07-07

### Added
- UI for connecting to backend on app cold start

### Changed
- Optimised Dockerfile to reduce image size
- Replaced `uv` runtime usage with standard `python` entrypoint

---

## [1.0.0-beta] - 2025-07-05

### Added
- Initial app release

---


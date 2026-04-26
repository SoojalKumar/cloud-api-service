---
title: Cloud-Based API Service
emoji: 🛠️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: FastAPI + React task manager with API keys, CI, and tests.
---

# Cloud-Based API Service

A small, production-flavored backend service (FastAPI + SQLite) with a React
dashboard bundled into the same image. This Space is auto-synced from the
canonical repo on GitHub on every push to `main`.

- **Source of truth / issues / tests**: <https://github.com/SoojalKumar/cloud-api-service>
- **OpenAPI docs**: `/docs` on this Space
- **Health probe**: `/api/v1/health`
- **Write API key for the demo**: `development-api-key` (paste into the UI to
  create, advance, or delete tasks). Data resets on container restart because
  the free Spaces tier has an ephemeral filesystem; every cold boot re-seeds
  three demo tasks so the UI is never empty.

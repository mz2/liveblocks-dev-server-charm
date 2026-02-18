# Implementation Plan: Liveblocks Dev Server K8s Juju Charm

**Branch**: `001-liveblocks-charm` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-liveblocks-charm/spec.md`

## Summary

Create a Kubernetes Juju charm to deploy and manage the Liveblocks dev server (`ghcr.io/liveblocks/dev-server`). The charm will provide automated deployment, configuration management, health monitoring, and ingress integration for WebSocket/HTTP traffic on port 1153. Built using the Ops framework in Python, following Charmhub best practices.

## Technical Context

**Language/Version**: Python 3.10+ (Juju Ops framework standard)
**Primary Dependencies**: ops (Juju Ops framework), charmcraft (build tooling), nginx-ingress-integrator (relation)
**Storage**: N/A (stateless workload)
**Testing**: pytest with ops.testing framework (unit), integration tests with juju-pytest
**Target Platform**: Kubernetes (via Juju K8s cloud)
**Project Type**: Single project (Juju charm)
**Performance Goals**: Charm achieves active status within 2 minutes; config changes applied within 60 seconds
**Constraints**: Container limits 128Mi memory, 100m CPU default; must support WebSocket connections
**Scale/Scope**: Single pod deployment; development environment use case

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS (No constitution principles defined - template placeholders only)

The constitution file contains only placeholder templates. No specific gates or principles are defined that would block this implementation. The charm follows standard Juju/Charmhub best practices as specified in FR-007.

## Project Structure

### Documentation (this feature)

```text
specs/001-liveblocks-charm/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
└── charm.py             # Main charm implementation

lib/
└── charms/              # Charm libraries (if any)

tests/
├── unit/
│   └── test_charm.py    # Unit tests using ops.testing
└── integration/
    └── test_charm.py    # Integration tests with juju-pytest

# Configuration files (root)
metadata.yaml            # Charm metadata (name, containers, relations)
config.yaml              # Charm configuration options
charmcraft.yaml          # Build configuration for charmcraft
requirements.txt         # Python dependencies
README.md                # Documentation with running instructions
```

**Structure Decision**: Standard Juju K8s charm layout following Charmhub conventions. Single `src/charm.py` for the charm logic since this is a straightforward OCI workload deployment. Tests separated into unit (ops.testing) and integration (juju-pytest) directories.

## Complexity Tracking

> No constitution violations to justify - template constitution has no defined gates.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

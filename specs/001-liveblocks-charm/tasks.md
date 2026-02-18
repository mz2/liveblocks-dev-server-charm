# Tasks: Liveblocks Dev Server K8s Juju Charm

**Input**: Design documents from `/specs/001-liveblocks-charm/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests included as the charm follows Juju best practices requiring unit tests for Charmhub publishing.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

**Build Environment**: All charmcraft and juju commands MUST run inside an Incus container (or VM as fallback).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Standard Juju K8s charm layout:
```
src/charm.py             # Main charm implementation
charmcraft.yaml          # Charm metadata, containers, relations, config
requirements.txt         # Python dependencies
tests/unit/test_charm.py # Unit tests
README.md                # Documentation
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and development environment setup

- [ ] T001 Create Incus container for development: `incus launch ubuntu:24.04 charm-builder`
- [ ] T002 Inside Incus container: Install charmcraft and LXD: `sudo snap install charmcraft --classic && sudo snap install lxd && lxd init --auto`
- [x] T003 [P] Create project directory structure per plan.md at repository root
- [x] T004 [P] Create requirements.txt with ops dependency at repository root
- [x] T005 [P] Create pyproject.toml with project configuration at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core charm infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create charmcraft.yaml with base configuration (name, type, base, platforms) per contracts/charmcraft.yaml
- [x] T007 Add container definition to charmcraft.yaml (liveblocks container, liveblocks-image resource)
- [x] T008 Create src/charm.py with basic CharmBase skeleton and `__init__` method
- [x] T009 Implement pebble_ready event handler skeleton in src/charm.py
- [x] T010 Add `if __name__ == "__main__": ops.main(CharmClass)` entry point to src/charm.py

**Checkpoint**: Foundation ready - charm can be packed (will not deploy yet)

---

## Phase 3: User Story 1 - Deploy Liveblocks Dev Server (Priority: P1) 🎯 MVP

**Goal**: Operators can deploy the Liveblocks dev server to K8s using Juju and see "active" status

**Independent Test**: Run `juju deploy ./liveblocks-dev-server_amd64.charm --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest` and verify charm reaches "active" status

### Tests for User Story 1

- [x] T011 [P] [US1] Create tests/unit/test_charm.py with test fixtures using ops.testing.Harness
- [x] T012 [P] [US1] Write unit test for pebble_ready event in tests/unit/test_charm.py
- [x] T013 [P] [US1] Write unit test for charm status transitions in tests/unit/test_charm.py

### Implementation for User Story 1

- [x] T014 [US1] Implement `_get_pebble_layer()` method in src/charm.py per contracts/pebble-layer.yaml
- [x] T015 [US1] Implement `_on_pebble_ready()` handler to add layer and start service in src/charm.py
- [x] T016 [US1] Add ActiveStatus and WaitingStatus handling in src/charm.py
- [ ] T017 [US1] Verify charm can be packed: run `charmcraft pack` in Incus container
- [ ] T018 [US1] Test deployment in Incus container: `juju deploy` and verify "active" status

**Checkpoint**: User Story 1 complete - charm deploys and shows active status

---

## Phase 4: User Story 2 - Configure Dev Server Settings (Priority: P2)

**Goal**: Operators can configure the charm via `juju config` and changes are applied gracefully

**Independent Test**: Deploy charm, run `juju config liveblocks-dev-server external-hostname=test.local`, verify config is applied

### Tests for User Story 2

- [x] T019 [P] [US2] Write unit test for config_changed event in tests/unit/test_charm.py
- [x] T020 [P] [US2] Write unit test for invalid config handling (BlockedStatus) in tests/unit/test_charm.py

### Implementation for User Story 2

- [x] T021 [US2] Add config options to charmcraft.yaml (external-hostname) per contracts/charmcraft.yaml
- [x] T022 [US2] Observe config_changed event in charm `__init__` in src/charm.py
- [x] T023 [US2] Implement `_on_config_changed()` handler in src/charm.py
- [x] T024 [US2] Add config validation logic with BlockedStatus for invalid values in src/charm.py
- [x] T025 [US2] Ensure `_on_config_changed()` calls `container.replan()` to apply changes in src/charm.py

**Checkpoint**: User Story 2 complete - configuration changes work

---

## Phase 5: User Story 3 - Access Dev Server from Applications (Priority: P2)

**Goal**: External clients can access the dev server via nginx-ingress-integrator relation

**Independent Test**: Deploy charm with nginx-ingress-integrator, create relation, verify HTTP/WebSocket access via ingress URL

### Tests for User Story 3

- [x] T026 [P] [US3] Write unit test for ingress relation initialization in tests/unit/test_charm.py
- [x] T027 [P] [US3] Write unit test for ingress data being set correctly in tests/unit/test_charm.py

### Implementation for User Story 3

- [x] T028 [US3] Add ingress relation to charmcraft.yaml requires section per contracts/ingress-relation.yaml
- [ ] T029 [US3] Fetch nginx-ingress-integrator library: `charmcraft fetch-lib charms.nginx_ingress_integrator.v0.ingress`
- [x] T030 [US3] Import IngressRequires in src/charm.py
- [x] T031 [US3] Initialize IngressRequires in charm `__init__` with service-hostname, service-name, service-port in src/charm.py
- [x] T032 [US3] Update ingress hostname when config changes (use external-hostname or app.name) in src/charm.py

**Checkpoint**: User Story 3 complete - ingress relation works

---

## Phase 6: User Story 4 - Understand and Use the Charm via Documentation (Priority: P2)

**Goal**: New users can deploy the charm by following README instructions without external help

**Independent Test**: Have someone unfamiliar with the charm follow README.md to successfully deploy

### Implementation for User Story 4

- [x] T033 [P] [US4] Create README.md with overview section (purpose, features, requirements)
- [x] T034 [P] [US4] Add Prerequisites section to README.md (Juju, K8s cloud, Incus for building)
- [x] T035 [US4] Add Build Instructions section to README.md (Incus container setup, charmcraft pack)
- [x] T036 [US4] Add Deployment section to README.md (juju deploy, resource specification)
- [x] T037 [US4] Add Configuration section to README.md with all config options and examples
- [x] T038 [US4] Add Ingress Setup section to README.md (nginx-ingress-integrator relation)
- [x] T039 [US4] Add Troubleshooting section to README.md (common issues, debug commands)
- [x] T040 [US4] Add Verification section to README.md (juju status, kubectl commands)

**Checkpoint**: User Story 4 complete - README enables self-service deployment

---

## Phase 7: User Story 5 - Monitor Dev Server Health (Priority: P3)

**Goal**: Operators see meaningful health status in `juju status` and charm reflects container health issues

**Independent Test**: Deploy charm, verify `juju status` shows health info; simulate failure and verify status updates

### Tests for User Story 5

- [x] T041 [P] [US5] Write unit test for update_status event in tests/unit/test_charm.py
- [x] T042 [P] [US5] Write unit test for health check failure handling in tests/unit/test_charm.py

### Implementation for User Story 5

- [x] T043 [US5] Add health checks to Pebble layer in `_get_pebble_layer()` per contracts/pebble-layer.yaml in src/charm.py
- [x] T044 [US5] Observe update_status event in charm `__init__` in src/charm.py
- [x] T045 [US5] Implement `_on_update_status()` to check service health and update status in src/charm.py
- [x] T046 [US5] Observe pebble_check_failed event in charm `__init__` in src/charm.py
- [x] T047 [US5] Implement `_on_pebble_check_failed()` to set BlockedStatus with error details in src/charm.py
- [x] T048 [US5] Observe pebble_check_recovered event and implement recovery handler in src/charm.py

**Checkpoint**: User Story 5 complete - health monitoring works

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements affecting multiple user stories

- [x] T049 [P] Add type hints to all methods in src/charm.py
- [x] T050 [P] Add docstrings to all public methods in src/charm.py
- [x] T051 [P] Add logging statements for key operations in src/charm.py
- [ ] T052 Run all unit tests: `python -m pytest tests/unit/` in Incus container
- [ ] T053 Run charmcraft lint: `charmcraft lint` in Incus container
- [ ] T054 Verify charm builds successfully: `charmcraft pack` in Incus container
- [ ] T055 Perform end-to-end validation per quickstart.md in Incus container
- [ ] T056 Update README.md with any changes discovered during testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Must complete first - establishes core deployment
  - US2 (P2): Can parallel with US3-US5 after US1
  - US3 (P2): Can parallel with US2, US4, US5 after US1
  - US4 (P2): Can parallel with US2, US3, US5 after US1
  - US5 (P3): Can start after US1
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundational only - No dependencies on other stories
- **User Story 2 (P2)**: Foundational + ideally US1 complete (for testing)
- **User Story 3 (P2)**: Foundational + ideally US1 complete (for relation testing)
- **User Story 4 (P2)**: Should have US1-US3 complete to document accurately
- **User Story 5 (P3)**: Foundational + ideally US1 complete (builds on Pebble layer)

### Within Each User Story

- Tests written first (TDD approach)
- Implementation tasks in dependency order
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005 can run in parallel
- **US1 Tests**: T011, T012, T013 can run in parallel
- **US2 Tests**: T019, T020 can run in parallel
- **US3 Tests**: T026, T027 can run in parallel
- **US4 Docs**: T033, T034 can run in parallel (initial sections)
- **US5 Tests**: T041, T042 can run in parallel
- **Polish**: T049, T050, T051 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T011 "Create tests/unit/test_charm.py with test fixtures"
Task: T012 "Write unit test for pebble_ready event"
Task: T013 "Write unit test for charm status transitions"

# Then implementation sequentially:
Task: T014 "Implement _get_pebble_layer()"
Task: T015 "Implement _on_pebble_ready()"
# etc.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Incus container, dependencies)
2. Complete Phase 2: Foundational (basic charm skeleton)
3. Complete Phase 3: User Story 1 (deployment works)
4. **STOP and VALIDATE**: `charmcraft pack` + `juju deploy` + verify "active"
5. Deploy/demo if ready - you have a working charm!

### Incremental Delivery

1. Setup + Foundational → Basic charm structure ready
2. Add User Story 1 → Charm deploys successfully (MVP!)
3. Add User Story 2 → Configuration works
4. Add User Story 3 → Ingress integration works
5. Add User Story 4 → Documentation complete
6. Add User Story 5 → Health monitoring works
7. Polish → Production-ready charm

### Single Developer Strategy

Execute phases 1-8 sequentially, completing each user story before starting the next.

---

## Notes

- **Build Environment**: All `charmcraft` and `juju` commands MUST run inside Incus container
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

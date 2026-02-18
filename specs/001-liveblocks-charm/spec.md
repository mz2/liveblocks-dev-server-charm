# Feature Specification: Liveblocks Dev Server K8s Juju Charm

**Feature Branch**: `001-liveblocks-charm`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "I would like to create a K8s Juju charm for the liveblocks dev server, which is available as ghcr.io/liveblocks/dev-server docker image now. You can build the charm out in an incus container with ubuntu."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Liveblocks Dev Server (Priority: P1)

As a platform operator, I want to deploy the Liveblocks dev server to my Kubernetes cluster using Juju so that my development team can use Liveblocks collaborative features in their applications without managing the infrastructure manually.

**Why this priority**: This is the core functionality - without successful deployment, no other features matter. Operators need a working charm before they can configure or integrate it.

**Independent Test**: Can be fully tested by running `juju deploy liveblocks-dev-server` against a K8s cloud and verifying the workload becomes active with the dev server responding to health checks.

**Acceptance Scenarios**:

1. **Given** a Juju controller connected to a Kubernetes cloud, **When** an operator deploys the liveblocks-dev-server charm, **Then** the charm creates a pod running the liveblocks dev server container and reports "active" status.
2. **Given** a deployed liveblocks-dev-server charm, **When** the container starts, **Then** the dev server becomes reachable on its designated port within the cluster.
3. **Given** a deployed liveblocks-dev-server charm, **When** the pod is terminated unexpectedly, **Then** Kubernetes restarts the pod and the charm recovers to active status.

---

### User Story 2 - Configure Dev Server Settings (Priority: P2)

As a platform operator, I want to configure the Liveblocks dev server through Juju configuration options so that I can customize its behavior without rebuilding or manually editing container settings.

**Why this priority**: Configuration is essential for adapting the dev server to different environments, but requires a working deployment first.

**Independent Test**: Can be tested by deploying the charm, modifying a configuration option via `juju config`, and verifying the change takes effect in the running container.

**Acceptance Scenarios**:

1. **Given** a deployed liveblocks-dev-server charm, **When** an operator sets a configuration option, **Then** the charm applies the configuration and the dev server reflects the change.
2. **Given** an invalid configuration value, **When** an operator attempts to apply it, **Then** the charm reports a blocked status with a clear error message explaining the issue.

---

### User Story 3 - Access Dev Server from Applications (Priority: P2)

As an application developer, I want my applications deployed in the same Kubernetes cluster to connect to the Liveblocks dev server so that I can build and test collaborative features locally.

**Why this priority**: Network accessibility is critical for the dev server to be useful, but it depends on having a working deployment first.

**Independent Test**: Can be tested by deploying the charm and a test application, then verifying the application can reach the dev server endpoint.

**Acceptance Scenarios**:

1. **Given** a deployed liveblocks-dev-server charm, **When** an application in the same namespace sends a request to the dev server service, **Then** the dev server responds successfully.
2. **Given** a deployed liveblocks-dev-server charm, **When** the charm exposes the service, **Then** the service is accessible via its Kubernetes service name.
3. **Given** a deployed charm related to nginx-ingress-integrator, **When** an external client connects via the ingress URL, **Then** both HTTP requests and WebSocket connections succeed.

---

### User Story 4 - Understand and Use the Charm via Documentation (Priority: P2)

As a new user or contributor, I want comprehensive documentation including a README and running instructions so that I can quickly understand how to deploy, configure, and troubleshoot the charm without prior knowledge.

**Why this priority**: Documentation is essential for adoption and usability. Without clear instructions, users cannot effectively deploy or maintain the charm.

**Independent Test**: Can be tested by having a new user follow the README instructions to successfully deploy the charm without additional assistance.

**Acceptance Scenarios**:

1. **Given** a user with no prior experience with this charm, **When** they read the README, **Then** they understand the charm's purpose, prerequisites, and how to get started.
2. **Given** a user following the running instructions, **When** they execute the documented steps, **Then** they successfully deploy a working Liveblocks dev server.
3. **Given** a user encountering a common issue, **When** they consult the documentation, **Then** they find troubleshooting guidance to resolve the problem.

---

### User Story 5 - Monitor Dev Server Health (Priority: P3)

As a platform operator, I want to monitor the health and status of the Liveblocks dev server so that I can quickly identify and respond to issues.

**Why this priority**: Monitoring is valuable for operational awareness but is not required for basic functionality.

**Independent Test**: Can be tested by deploying the charm and running `juju status` to verify health information is displayed correctly.

**Acceptance Scenarios**:

1. **Given** a deployed liveblocks-dev-server charm, **When** an operator runs `juju status`, **Then** the charm displays meaningful status information including workload health.
2. **Given** a deployed charm where the dev server becomes unhealthy, **When** health checks fail, **Then** the charm updates its status to reflect the issue.

---

### Edge Cases

- What happens when the container image cannot be pulled (network issues, authentication required)?
- How does the charm handle insufficient cluster resources (CPU/memory limits)?
- What happens when configuration changes are applied while the dev server is handling active connections?
- How does the charm behave during Kubernetes node failures or rescheduling?
- How are active WebSocket connections affected when the ingress relation is added or removed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The charm MUST deploy the `ghcr.io/liveblocks/dev-server` container image to Kubernetes
- **FR-002**: The charm MUST create a Kubernetes service to expose the dev server within the cluster
- **FR-003**: The charm MUST report accurate workload status (active, blocked, waiting, maintenance)
- **FR-004**: The charm MUST support configuration options for customizing dev server behavior
- **FR-005**: The charm MUST implement health checks to monitor dev server availability
- **FR-006**: The charm MUST handle configuration changes gracefully without requiring full redeployment
- **FR-007**: The charm MUST follow Juju charm best practices and Charmhub publishing standards
- **FR-008**: The charm MUST be buildable in an Ubuntu environment; all charmcraft and juju commands MUST be executed inside an Incus container (or VM as fallback)
- **FR-009**: The charm MUST expose the dev server port (default: 1153)
- **FR-015**: The charm MUST support an ingress relation for integration with nginx-ingress-integrator to enable external access
- **FR-016**: The ingress configuration MUST support both HTTP and WebSocket connections over the same port
- **FR-017**: The charm MUST set default container resource limits (128Mi memory, 100m CPU) with configurable overrides

### Documentation Requirements

- **FR-010**: The charm MUST include a README file that documents the charm's purpose, features, and prerequisites
- **FR-011**: The README MUST include step-by-step running instructions for deploying the charm
- **FR-012**: The documentation MUST include configuration options and their descriptions
- **FR-013**: The documentation MUST include troubleshooting guidance for common issues
- **FR-014**: The documentation MUST include build instructions for developers, specifying that all charmcraft and juju commands run inside an Incus container (or VM as fallback)

### Key Entities

- **Charm**: The Juju K8s charm package that encapsulates deployment logic, configuration handling, and lifecycle management for the Liveblocks dev server
- **Workload Container**: The `ghcr.io/liveblocks/dev-server` OCI container running the actual Liveblocks dev server process
- **Kubernetes Service**: The cluster networking resource that exposes the dev server pod to other applications
- **Configuration Options**: User-definable settings that control dev server behavior (port, logging, etc.)
- **README Documentation**: The primary documentation file containing usage instructions, configuration reference, and troubleshooting guidance

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can deploy a working Liveblocks dev server with a single `juju deploy` command in under 5 minutes
- **SC-002**: The charm achieves "active" status within 2 minutes of deployment on a healthy cluster
- **SC-003**: Applications in the same Kubernetes namespace can successfully connect to the dev server within 30 seconds of the charm becoming active
- **SC-004**: Configuration changes are applied and reflected in the running workload within 60 seconds
- **SC-005**: The charm correctly identifies and reports container health issues within 30 seconds of occurrence
- **SC-006**: The charm passes Charmhub quality checks and can be published for community use
- **SC-007**: A new user can successfully deploy the charm by following only the README instructions, without external assistance
- **SC-008**: All configuration options are documented with descriptions and example values

## Clarifications

### Session 2026-02-17

- Q: Should the charm support Juju relations for integration with other charms? → A: Yes, ingress relation to integrate with nginx-ingress-integrator for external access. Dev server supports both WebSocket and HTTP over port 1153.
- Q: What container resource limits should be set by default? → A: Minimal defaults (128Mi memory, 100m CPU) suitable for dev environments.
- Q: Where should charmcraft and juju commands be executed? → A: All charmcraft and juju commands must run inside an Incus container (or VM as fallback if container doesn't work).

## Assumptions

- The `ghcr.io/liveblocks/dev-server` container image is publicly accessible without authentication
- The Liveblocks dev server is stateless and does not require persistent storage
- The target Kubernetes cluster has sufficient resources to run a single dev server pod
- Operators have a working Juju controller connected to a Kubernetes cloud
- The build environment is an Incus container (or VM as fallback) running Ubuntu with network access to download charm dependencies
- All charmcraft and juju commands are executed within the Incus container/VM, not on the host system
- The dev server uses both HTTP and WebSocket protocols for client connections over port 1153

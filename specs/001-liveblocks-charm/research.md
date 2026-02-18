# Research: Liveblocks Dev Server K8s Juju Charm

**Date**: 2026-02-17
**Feature**: 001-liveblocks-charm

## 1. Juju K8s Charm Structure

**Decision**: Use standard charmcraft-based structure with `charmcraft.yaml` as single source of truth

**Rationale**: Charmcraft automatically generates `metadata.yaml`, `config.yaml`, and `actions.yaml` from `charmcraft.yaml`, reducing duplication and maintenance overhead.

**Required Files**:
```
liveblocks-dev-server/
├── charmcraft.yaml        # Main configuration (containers, resources, config, relations)
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Python dependencies (must include 'ops')
├── src/
│   └── charm.py           # Main charm entrypoint
├── tests/
│   ├── unit/
│   │   └── test_charm.py
│   └── integration/
│       └── test_charm.py
└── lib/                   # Charm libraries (auto-fetched via charmcraft)
```

**Alternatives considered**:
- Separate metadata.yaml + config.yaml: Rejected because charmcraft.yaml consolidates these, reducing maintenance

---

## 2. Ops Framework for K8s Charms

**Decision**: Use ops framework v2.10+ with standard event handlers

**Rationale**: ops is the official Juju Python framework maintained by Canonical, providing type-safe APIs for charm development.

**Key Implementation Patterns**:

```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        framework.observe(self.on["container_name"].pebble_ready, self._on_pebble_ready)
        framework.observe(self.on.config_changed, self._on_config_changed)
        framework.observe(self.on.update_status, self._on_update_status)
```

**Status Classes**:
| Status | Usage |
|--------|-------|
| `ops.ActiveStatus()` | Charm is ready and operational |
| `ops.WaitingStatus("msg")` | Waiting for something (Pebble, relation) |
| `ops.BlockedStatus("msg")` | Blocked, requires user action |
| `ops.MaintenanceStatus("msg")` | Performing maintenance tasks |

**Critical Notes**:
- Charm class is re-instantiated on every event - no mutable state in memory
- Always check `container.can_connect()` before Pebble operations

---

## 3. OCI Workload Deployment via Pebble

**Decision**: Use Pebble layers to manage the workload container

**Rationale**: Pebble is injected into every K8s charm workload container, providing process management, health checks, and configuration without modifying the upstream container image.

**Container Definition in charmcraft.yaml**:
```yaml
containers:
  liveblocks:
    resource: liveblocks-image

resources:
  liveblocks-image:
    type: oci-image
    description: Liveblocks dev server OCI image
    upstream-source: ghcr.io/liveblocks/dev-server:latest
```

**Pebble Layer Configuration**:
```python
def _get_pebble_layer(self) -> ops.pebble.Layer:
    return ops.pebble.Layer({
        "summary": "liveblocks dev server",
        "services": {
            "liveblocks": {
                "override": "replace",
                "command": "/entrypoint.sh",  # Container's default entrypoint
                "startup": "enabled",
                "on-success": "restart",
                "on-failure": "restart",
            }
        },
    })
```

**Resource Limits**: Set at deploy time via Juju constraints, not in charm code:
```bash
juju deploy ./charm.charm --constraints "mem=128M cpu-power=100"
```

---

## 4. nginx-ingress-integrator Relation

**Decision**: Use `charms.nginx_ingress_integrator.v0.ingress` library for ingress integration

**Rationale**: Standard Canonical library providing clean abstraction over nginx-ingress configuration. Supports WebSocket connections automatically when configured correctly.

**Implementation**:

1. Add to charmcraft.yaml:
```yaml
requires:
  ingress:
    interface: ingress
```

2. Fetch library:
```bash
charmcraft fetch-lib charms.nginx_ingress_integrator.v0.ingress
```

3. Use in charm:
```python
from charms.nginx_ingress_integrator.v0.ingress import IngressRequires

class MyCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        self.ingress = IngressRequires(
            self,
            {
                "service-hostname": self.app.name,
                "service-name": self.app.name,
                "service-port": 1153,
            },
        )
```

**WebSocket Support**: nginx-ingress-integrator supports WebSocket connections by default when the backend service uses WebSocket. No special configuration required for the dev server's combined HTTP/WebSocket protocol.

---

## 5. Health Checks via Pebble

**Decision**: Implement HTTP health check on port 1153

**Rationale**: Pebble health checks map directly to Kubernetes liveness/readiness probes, providing automatic pod restart on failure.

**Implementation**:
```python
"checks": {
    "ready": {
        "override": "replace",
        "level": "ready",
        "period": "10s",
        "timeout": "3s",
        "threshold": 3,
        "tcp": {
            "port": 1153,
        },
    },
}
```

**Note**: Using TCP check on port 1153 since we don't have confirmed HTTP health endpoint. The dev server listens on this port for both HTTP and WebSocket traffic.

**Check Levels**:
- `alive`: Maps to Kubernetes liveness probe (restart on failure)
- `ready`: Maps to Kubernetes readiness probe (remove from service on failure)

---

## 6. Building with Charmcraft

**Decision**: Build using `charmcraft pack` with LXD provider (default)

**Rationale**: LXD provides clean, isolated build environment. Can use `--destructive-mode` in Incus container if needed.

**Build Process**:
```bash
# In Ubuntu environment (Incus container)
sudo snap install charmcraft --classic
sudo snap install lxd
lxd init --auto

# Build
charmcraft pack

# Deploy
juju deploy ./liveblocks-dev-server_amd64.charm \
    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest
```

**Incus Compatibility**: If building in an Incus container:
- Option 1: Use `charmcraft pack --destructive-mode` to build directly (no nested virtualization)
- Option 2: Configure LXD inside Incus if nesting is enabled

---

## 7. Configuration Options

**Decision**: Expose minimal configuration options for dev server customization

**Configuration in charmcraft.yaml**:
```yaml
config:
  options:
    external-hostname:
      default: ""
      type: string
      description: External hostname for ingress. If empty, uses app name.
    memory-limit:
      default: "128Mi"
      type: string
      description: Memory limit for the container (e.g., 128Mi, 256Mi)
    cpu-limit:
      default: "100m"
      type: string
      description: CPU limit for the container (e.g., 100m, 500m)
```

**Note**: Resource limits are advisory in config but actual enforcement is via Juju constraints at deploy time.

---

## Summary of Technical Decisions

| Area | Decision |
|------|----------|
| Project structure | charmcraft.yaml-based with src/charm.py |
| Framework | ops >= 2.10 |
| Container management | Pebble layers |
| Health checks | TCP check on port 1153 |
| Ingress | nginx-ingress-integrator relation |
| Build | charmcraft pack (LXD or destructive-mode) |
| Base | ubuntu@24.04 |

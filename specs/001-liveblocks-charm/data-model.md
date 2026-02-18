# Data Model: Liveblocks Dev Server K8s Juju Charm

**Date**: 2026-02-17
**Feature**: 001-liveblocks-charm

## Overview

This document defines the data structures and configuration schema for the Liveblocks Dev Server Juju charm. Since the charm manages a stateless workload, the "data model" primarily covers configuration entities and relation data.

---

## 1. Charm Configuration Schema

### Configuration Options

| Option | Type | Default | Description | Validation |
|--------|------|---------|-------------|------------|
| `external-hostname` | string | `""` | Hostname for ingress. If empty, uses app name | Valid hostname or empty |

### Example Configuration

```yaml
# config.yaml (auto-generated from charmcraft.yaml)
options:
  external-hostname:
    default: ""
    type: string
    description: |
      External hostname for ingress configuration.
      If left empty, the application name will be used.
```

---

## 2. Container Resource Configuration

Resource limits are managed via Juju constraints at deploy time, not charm configuration.

| Resource | Default | Range | Description |
|----------|---------|-------|-------------|
| Memory | 128Mi | 64Mi - 512Mi | Container memory limit |
| CPU | 100m | 50m - 500m | Container CPU limit (millicores) |

### Deploy-time Configuration

```bash
juju deploy liveblocks-dev-server \
    --constraints "mem=128M cpu-power=100"
```

---

## 3. Pebble Service Configuration

### Service Definition

| Field | Value | Description |
|-------|-------|-------------|
| name | `liveblocks` | Pebble service name |
| command | Container entrypoint | Starts the dev server |
| startup | `enabled` | Starts automatically |
| port | 1153 | Fixed port (not configurable) |

### Health Check Definition

| Field | Value | Description |
|-------|-------|-------------|
| name | `ready` | Check identifier |
| type | TCP | Connection check type |
| port | 1153 | Port to check |
| level | `ready` | Maps to K8s readiness probe |
| period | 10s | Check interval |
| timeout | 3s | Max wait time |
| threshold | 3 | Failures before unhealthy |

---

## 4. Relation Data Schema

### Ingress Relation (requires)

**Interface**: `ingress`
**Direction**: Requires (charm → nginx-ingress-integrator)

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `service-hostname` | string | Config or app name | External hostname |
| `service-name` | string | App name | K8s service name |
| `service-port` | int | 1153 | Port to expose |

### Relation Data Flow

```
┌─────────────────────┐         ┌──────────────────────────┐
│  liveblocks-charm   │         │  nginx-ingress-integrator │
│                     │         │                          │
│  relation data:     │────────►│  Creates:                │
│  - service-hostname │         │  - Ingress resource      │
│  - service-name     │         │  - Routes traffic to     │
│  - service-port     │         │    service:1153          │
└─────────────────────┘         └──────────────────────────┘
```

---

## 5. Kubernetes Resources (Generated)

The charm, via Juju, creates these Kubernetes resources:

### Pod Specification

```yaml
# Conceptual - managed by Juju
apiVersion: v1
kind: Pod
metadata:
  name: liveblocks-dev-server-0
  labels:
    app.kubernetes.io/name: liveblocks-dev-server
spec:
  containers:
    - name: liveblocks
      image: ghcr.io/liveblocks/dev-server:latest
      ports:
        - containerPort: 1153
      resources:
        limits:
          memory: "128Mi"
          cpu: "100m"
```

### Service Specification

```yaml
# Conceptual - managed by Juju
apiVersion: v1
kind: Service
metadata:
  name: liveblocks-dev-server
spec:
  selector:
    app.kubernetes.io/name: liveblocks-dev-server
  ports:
    - port: 1153
      targetPort: 1153
      protocol: TCP
  type: ClusterIP
```

---

## 6. State Transitions

### Charm Status State Machine

```
                    ┌─────────────────┐
                    │    UNKNOWN      │
                    │  (initial)      │
                    └────────┬────────┘
                             │ charm install
                             ▼
                    ┌─────────────────┐
                    │    WAITING      │
           ┌───────►│ "Waiting for    │
           │        │    Pebble"      │
           │        └────────┬────────┘
           │                 │ pebble_ready
           │                 ▼
           │        ┌─────────────────┐
           │        │   MAINTENANCE   │◄──────┐
           │        │ "Configuring"   │       │
           │        └────────┬────────┘       │
           │                 │ config applied │ config_changed
           │                 ▼                │
           │        ┌─────────────────┐       │
           │        │     ACTIVE      │───────┘
           │        │ "Ready"         │
           │        └────────┬────────┘
           │                 │ health check fail
           │                 ▼
           │        ┌─────────────────┐
           └────────┤    BLOCKED      │
     restart/       │ "Health check   │
     recover        │  failed"        │
                    └─────────────────┘
```

### Valid Status Transitions

| From | To | Trigger |
|------|----|---------|
| UNKNOWN | WAITING | Charm installed |
| WAITING | ACTIVE | Pebble ready, service started |
| ACTIVE | MAINTENANCE | Config change in progress |
| MAINTENANCE | ACTIVE | Config applied successfully |
| ACTIVE | BLOCKED | Health check failure |
| BLOCKED | ACTIVE | Health check recovery |
| BLOCKED | WAITING | Container restart |

---

## 7. Entity Relationships

```
┌────────────────────┐
│      Charm         │
│  (CharmBase)       │
└─────────┬──────────┘
          │ manages
          ▼
┌────────────────────┐      ┌────────────────────┐
│     Container      │      │   IngressRequires  │
│   "liveblocks"     │      │     (relation)     │
└─────────┬──────────┘      └─────────┬──────────┘
          │ runs                      │ provides to
          ▼                           ▼
┌────────────────────┐      ┌────────────────────┐
│  Pebble Service    │      │  nginx-ingress     │
│   "liveblocks"     │      │   -integrator      │
└─────────┬──────────┘      └────────────────────┘
          │ exposes
          ▼
┌────────────────────┐
│   K8s Service      │
│    port: 1153      │
└────────────────────┘
```

---

## Summary

| Entity | Type | Persistence |
|--------|------|-------------|
| Charm config | YAML schema | Juju controller |
| Container resources | K8s constraints | Juju model |
| Pebble layer | Runtime config | In-memory |
| Relation data | Key-value | Juju controller |
| K8s Service | Resource | K8s cluster |

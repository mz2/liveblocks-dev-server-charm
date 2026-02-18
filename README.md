# K8s charm for Liveblocks dev server

A Kubernetes Juju charm that deploys the [Liveblocks](https://liveblocks.io/) development server.

Liveblocks is a platform for building collaborative applications. This charm deploys the development server which provides a local environment for testing Liveblocks features without connecting to the production Liveblocks service.

A single dev server instance maps to one Liveblocks [room](https://liveblocks.io/docs/concepts)—the space where users collaborate on shared documents, diagrams, or other artifacts.

## Features

- Automated deployment to Kubernetes via Juju
- Health monitoring and automatic recovery
- Ingress integration for external access via traefik-k8s
- Support for both HTTP and WebSocket connections on port 1153

## Quick Start

### 1. Set up Juju with Kubernetes using Concierge

[Concierge](https://github.com/canonical/concierge) provisions a complete Juju + Kubernetes environment:

```bash
sudo snap install --classic concierge
sudo concierge prepare -p k8s
```

### 2. Deploy the charm

```bash
juju add-model liveblocks
juju deploy liveblocks-dev-server --channel=edge
```

### 3. Verify deployment

```bash
juju status
```

Expected output:
```
Model       Controller  Cloud/Region  Version  SLA          Timestamp
liveblocks  my-k8s      my-k8s        3.6.14   unsupported  13:09:22Z

App                    Version  Status  Scale  Charm                  Channel      Rev  Address         Exposed  Message
liveblocks-dev-server           active      1  liveblocks-dev-server  latest/edge    1  10.152.183.212  no

Unit                      Workload  Agent  Address     Ports  Message
liveblocks-dev-server/0*  active    idle   10.1.0.138
```

### 4. Test the service

```bash
# Get the pod IP
POD_IP=$(kubectl get pod -l app.kubernetes.io/name=liveblocks-dev-server \
  -n liveblocks -o jsonpath='{.items[0].status.podIP}')

# Create a room (use sk_localdev as the secret key for the dev server)
curl -s -X POST "http://${POD_IP}:1153/v2/rooms" \
  -H 'Authorization: Bearer sk_localdev' \
  -H 'Content-Type: application/json' \
  -d '{"id":"my-room"}'
```

Expected output:
```json
{"type":"room","id":"my-room","createdAt":"2026-02-18T12:08:11.552Z","metadata":{},"defaultAccesses":["room:write"],"groupsAccesses":{},"usersAccesses":{}}
```

List rooms:
```bash
curl -s "http://${POD_IP}:1153/v2/rooms" \
  -H 'Authorization: Bearer sk_localdev'
```

---

## Prerequisites

- **Kubernetes cluster** (Canonical K8s or MicroK8s)
- **Juju 3.x** with a Kubernetes cloud configured

## Build Instructions

### 1. Install build tools with Concierge

```bash
sudo snap install --classic concierge
sudo concierge prepare -p charmcraft
```

### 2. Clone and build

```bash
git clone https://github.com/mz2/liveblocks-dev-server-charm.git
cd liveblocks-dev-server-charm

# Fetch required charm libraries
charmcraft fetch-lib charms.traefik_k8s.v2.ingress

# Build the charm
charmcraft pack
```

This produces a file like `liveblocks-dev-server_amd64.charm`.

## Deployment

### Basic Deployment

```bash
# Deploy to your Kubernetes model
juju deploy ./liveblocks-dev-server_amd64.charm \
    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest

# Monitor deployment
juju status --watch 2s
```

## Ingress Setup

To enable external access to the dev server, integrate with traefik-k8s:

```bash
# Deploy traefik-k8s
juju deploy traefik-k8s --trust

# Create the relation
juju relate liveblocks-dev-server traefik-k8s
```

Check the ingress URL:
```bash
juju run traefik-k8s/0 show-proxied-endpoints
```

## Troubleshooting

### View Charm Logs

```bash
juju debug-log --include liveblocks-dev-server
```

### View Container Logs

```bash
juju ssh liveblocks-dev-server/0 -- pebble logs liveblocks -f
```

## Development

### Running Unit Tests

```bash
# Install test dependencies
pip install pytest ops

# Run tests
python -m pytest tests/unit/ -v
```

## License

See [LICENSE](LICENSE) file for details.

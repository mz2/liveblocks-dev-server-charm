# Liveblocks Dev Server Kubernetes Charm

A Kubernetes Juju charm that deploys the [Liveblocks](https://liveblocks.io/) development server.

Liveblocks is a platform for building collaborative applications. This charm deploys the development server which provides a local environment for testing Liveblocks features without connecting to the production Liveblocks service.

## Features

- Automated deployment to Kubernetes via Juju
- Health monitoring and automatic recovery
- Ingress integration for external access via nginx-ingress-integrator
- Support for both HTTP and WebSocket connections on port 1153
- Configurable external hostname for ingress

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
juju deploy ./liveblocks-dev-server_amd64.charm \
  --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest
```

### 3. Verify deployment

```bash
juju status
```

Expected output:
```
Model       Controller  Cloud/Region  Version  SLA          Timestamp
liveblocks  my-k8s      my-k8s        3.6.14   unsupported  11:49:08Z

App                    Version  Status  Scale  Charm                  Channel  Rev  Address        Exposed  Message
liveblocks-dev-server           active      1  liveblocks-dev-server             0  10.152.183.22  no

Unit                      Workload  Agent  Address     Ports  Message
liveblocks-dev-server/0*  active    idle   10.1.0.146
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

- **Juju 3.x** with a Kubernetes cloud configured
- **Kubernetes cluster** (Canonical K8s or MicroK8s)
- **LXD** for VM-based testing (Ubuntu 24.04 recommended)

## Build Instructions

All charmcraft and juju commands **must** run inside an LXD container (or VM as fallback).

### 1. Create Build Environment

```bash
# Create an Ubuntu container for building
lxc launch ubuntu:24.04 charm-builder
lxc exec charm-builder -- bash
```

### 2. Install Build Dependencies

```bash
# Inside the Incus container
sudo snap install charmcraft --classic
sudo snap install lxd
sudo lxd init --auto
```

### 3. Clone and Build

```bash
# Clone the repository
git clone <repository-url>
cd liveblocks-dev-server-charm

# Fetch required charm libraries
charmcraft fetch-lib charms.nginx_ingress_integrator.v0.ingress

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

### Deployment with Resource Constraints

```bash
juju deploy ./liveblocks-dev-server_amd64.charm \
    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest \
    --constraints "mem=128M cpu-power=100"
```

## Configuration

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `external-hostname` | string | `""` | External hostname for ingress. If empty, uses the application name. |

### View Configuration

```bash
juju config liveblocks-dev-server
```

### Change Configuration

```bash
# Set external hostname for ingress
juju config liveblocks-dev-server external-hostname=liveblocks.example.com
```

## Ingress Setup

To enable external access to the dev server, integrate with nginx-ingress-integrator:

```bash
# Deploy nginx-ingress-integrator
juju deploy nginx-ingress-integrator
juju trust nginx-ingress-integrator --scope cluster

# Set your desired hostname
juju config liveblocks-dev-server external-hostname=liveblocks.local

# Create the relation
juju relate liveblocks-dev-server nginx-ingress-integrator

# Verify ingress is created
kubectl get ingress -n <model-namespace>
```

### Testing External Access

```bash
# Add hostname to /etc/hosts (if using local hostname)
echo "127.0.0.1 liveblocks.local" | sudo tee -a /etc/hosts

# Test HTTP
curl http://liveblocks.local/

# Test WebSocket (requires wscat: npm install -g wscat)
wscat -c ws://liveblocks.local/
```

## Verification

### Check Charm Status

```bash
juju status
```

Expected output when healthy:
```
Model    Controller  Cloud/Region        Version  SLA          Timestamp
mymodel  myctrl      microk8s/localhost  3.x.x    unsupported  12:00:00Z

App                      Version  Status  Scale  Charm                    Channel  Rev  Address
liveblocks-dev-server             active      1  liveblocks-dev-server             0    10.1.x.x

Unit                        Workload  Agent  Address     Ports  Message
liveblocks-dev-server/0*    active    idle   10.1.x.x
```

### Test In-Cluster Connectivity

```bash
# Get the service IP
kubectl get svc -n <model-namespace> liveblocks-dev-server

# Test from within the cluster
kubectl run -it --rm test-pod --image=curlimages/curl -- \
    curl http://liveblocks-dev-server:1153/
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

### Check Pebble Services

```bash
juju ssh liveblocks-dev-server/0 -- pebble services
```

### Check Health Status

```bash
juju ssh liveblocks-dev-server/0 -- pebble checks
```

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Image pull failure | Status: `waiting` | Verify image name and registry access |
| Insufficient resources | Pod not scheduling | Reduce constraints or increase cluster capacity |
| Ingress not working | 404 or connection refused | Check `juju relate` status, verify nginx-ingress-integrator is active |
| Pebble not ready | Status: `waiting` | Wait for container to start, check pod events with `kubectl describe pod` |

### Debug Commands

```bash
# Get pod details
kubectl get pods -n <model-namespace> -l app.kubernetes.io/name=liveblocks-dev-server

# Describe pod for events
kubectl describe pod -n <model-namespace> <pod-name>

# Check Juju model status
juju status --relations

# View relation data
juju show-unit liveblocks-dev-server/0
```

## Cleanup

```bash
# Remove the application
juju remove-application liveblocks-dev-server

# Remove ingress (if deployed)
juju remove-application nginx-ingress-integrator
```

## Development

### Running Unit Tests

```bash
# Install test dependencies
pip install pytest ops

# Run tests
python -m pytest tests/unit/ -v
```

### Building for Development

```bash
# Build without LXD (destructive mode)
charmcraft pack --destructive-mode
```

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING](CONTRIBUTING.md) guide for details.

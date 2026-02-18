# Quickstart: Liveblocks Dev Server K8s Juju Charm

## Prerequisites

- Ubuntu 22.04 or 24.04 (for building)
- Juju 3.x with a Kubernetes cloud configured
- Access to Kubernetes cluster (MicroK8s, EKS, GKE, etc.)

## Build the Charm

### Option 1: Build in Incus/LXD Container (Recommended)

```bash
# Create Ubuntu container
incus launch ubuntu:24.04 charm-builder
incus exec charm-builder -- bash

# Inside container: Install dependencies
sudo snap install charmcraft --classic
sudo snap install lxd
sudo lxd init --auto

# Clone and build
git clone <repository-url>
cd liveblocks-dev-server-charm
charmcraft pack
```

### Option 2: Build Directly (Destructive Mode)

```bash
# On Ubuntu host with charmcraft installed
charmcraft pack --destructive-mode
```

## Deploy the Charm

### 1. Basic Deployment

```bash
# Deploy to Kubernetes model
juju deploy ./liveblocks-dev-server_amd64.charm \
    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest

# Check status
juju status --watch 2s
```

### 2. Deployment with Resource Constraints

```bash
juju deploy ./liveblocks-dev-server_amd64.charm \
    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest \
    --constraints "mem=128M cpu-power=100"
```

### 3. Add Ingress for External Access

```bash
# Deploy nginx-ingress-integrator
juju deploy nginx-ingress-integrator
juju trust nginx-ingress-integrator --scope cluster

# Configure hostname and relate
juju config liveblocks-dev-server external-hostname=liveblocks.local
juju relate liveblocks-dev-server nginx-ingress-integrator

# Verify ingress is created
kubectl get ingress -n <model-namespace>
```

## Verify Deployment

### Check Charm Status

```bash
juju status
```

Expected output:
```
Model    Controller  Cloud/Region        Version  SLA          Timestamp
mymodel  myctrl      microk8s/localhost  3.x.x    unsupported  12:00:00Z

App                      Version  Status  Scale  Charm                    Channel  Rev  Address
liveblocks-dev-server             active      1  liveblocks-dev-server             0    10.1.x.x

Unit                        Workload  Agent  Address     Ports  Message
liveblocks-dev-server/0*    active    idle   10.1.x.x
```

### Test Connectivity (In-Cluster)

```bash
# Get service IP
kubectl get svc -n <model-namespace> liveblocks-dev-server

# Test from within cluster
kubectl run -it --rm test-pod --image=curlimages/curl -- \
    curl http://liveblocks-dev-server:1153/
```

### Test Connectivity (Via Ingress)

```bash
# Add to /etc/hosts if using local hostname
echo "127.0.0.1 liveblocks.local" | sudo tee -a /etc/hosts

# Test HTTP
curl http://liveblocks.local/

# Test WebSocket (requires wscat: npm install -g wscat)
wscat -c ws://liveblocks.local/
```

## Configuration

### View Current Configuration

```bash
juju config liveblocks-dev-server
```

### Change Configuration

```bash
# Set external hostname for ingress
juju config liveblocks-dev-server external-hostname=myapp.example.com
```

## Troubleshooting

### View Logs

```bash
# Charm logs
juju debug-log --include liveblocks-dev-server

# Container logs
juju ssh liveblocks-dev-server/0 -- \
    pebble logs liveblocks -f
```

### Check Pebble Services

```bash
juju ssh liveblocks-dev-server/0 -- \
    pebble services
```

### Check Health

```bash
juju ssh liveblocks-dev-server/0 -- \
    pebble checks
```

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Image pull failure | Status: `waiting` | Verify image name and registry access |
| Insufficient resources | Pod not scheduling | Reduce constraints or increase cluster capacity |
| Ingress not working | 404 or connection refused | Check `juju relate` status, verify nginx-ingress-integrator is active |

## Cleanup

```bash
# Remove application
juju remove-application liveblocks-dev-server

# Remove ingress (if deployed)
juju remove-application nginx-ingress-integrator
```

## Next Steps

- Configure TLS on nginx-ingress-integrator for HTTPS
- Scale horizontally with `juju add-unit` (if supported by workload)
- Integrate with observability stack (Prometheus, Grafana)

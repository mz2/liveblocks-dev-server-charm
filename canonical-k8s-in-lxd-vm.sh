#!/bin/bash
# Setup script for creating an LXD VM with Canonical K8s and Juju
# ready for charm deployment

set -e

VM_NAME="${1:-liveblocks-dev-server}"

echo "==> Creating LXD VM: $VM_NAME"
lxc launch ubuntu:24.04 "$VM_NAME" --vm \
  -c limits.cpu=4 -c limits.memory=8GiB -d root,size=30GiB

echo "==> Waiting for VM to be ready..."
sleep 30

echo "==> Installing dependencies..."
lxc exec "$VM_NAME" -- bash -c "apt-get update && apt-get install -y snapd curl"
lxc exec "$VM_NAME" -- bash -c "snap install k8s --classic --channel=1.32-classic/stable"
lxc exec "$VM_NAME" -- bash -c "snap install juju --channel=3/stable"

echo "==> Bootstrapping Kubernetes..."
lxc exec "$VM_NAME" -- k8s bootstrap
lxc exec "$VM_NAME" -- k8s status --wait-ready --timeout 3m

echo "==> Configuring Juju..."
lxc exec "$VM_NAME" -- bash -c "mkdir -p ~/.kube ~/.local/share/juju && k8s config > ~/.kube/config"
lxc exec "$VM_NAME" -- bash -c "juju add-k8s my-k8s --client"
lxc exec "$VM_NAME" -- bash -c "juju bootstrap my-k8s"
lxc exec "$VM_NAME" -- bash -c "juju add-model liveblocks"

echo "==> Setup complete!"
echo ""
echo "To deploy the charm:"
echo "  lxc file push liveblocks-dev-server_amd64.charm $VM_NAME/root/"
echo "  lxc exec $VM_NAME -- juju deploy ./liveblocks-dev-server_amd64.charm \\"
echo "    --resource liveblocks-image=ghcr.io/liveblocks/dev-server:latest"
echo ""
echo "To check status:"
echo "  lxc exec $VM_NAME -- juju status"

#!/usr/bin/env python3
"""Liveblocks Dev Server Kubernetes Charm."""

import logging

import ops

logger = logging.getLogger(__name__)

LIVEBLOCKS_PORT = 1153

# Import ingress library if available (fetched via charmcraft fetch-lib)
try:
    from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
    INGRESS_AVAILABLE = True
except ImportError:
    INGRESS_AVAILABLE = False
    IngressPerAppRequirer = None


class LiveblocksDevServerCharm(ops.CharmBase):
    """Charm for deploying and managing the Liveblocks development server."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        framework.observe(self.on["liveblocks"].pebble_ready, self._on_pebble_ready)
        framework.observe(self.on.config_changed, self._on_config_changed)
        framework.observe(self.on.update_status, self._on_update_status)
        framework.observe(self.on["liveblocks"].pebble_check_failed, self._on_pebble_check_failed)
        framework.observe(self.on["liveblocks"].pebble_check_recovered, self._on_pebble_check_recovered)

        # Initialize ingress relation if library is available
        if INGRESS_AVAILABLE:
            self.ingress = IngressPerAppRequirer(self, port=LIVEBLOCKS_PORT)
        else:
            self.ingress = None

    def _get_pebble_layer(self) -> ops.pebble.Layer:
        """Return the Pebble layer configuration for the workload."""
        return ops.pebble.Layer({
            "summary": "liveblocks dev server layer",
            "description": "Pebble configuration for the Liveblocks development server",
            "services": {
                "liveblocks": {
                    "override": "replace",
                    "summary": "Liveblocks development server",
                    "command": "/usr/local/bin/bun /app/node_modules/liveblocks/dist/index.js dev --port 1153",
                    "working-dir": "/app",
                    "startup": "enabled",
                    "on-success": "restart",
                    "on-failure": "restart",
                    "backoff-delay": "1s",
                    "backoff-factor": 2.0,
                    "backoff-limit": "30s",
                },
            },
            "checks": {
                "ready": {
                    "override": "replace",
                    "level": "ready",
                    "period": "10s",
                    "timeout": "3s",
                    "threshold": 3,
                    "tcp": {
                        "port": LIVEBLOCKS_PORT,
                    },
                },
                "alive": {
                    "override": "replace",
                    "level": "alive",
                    "period": "30s",
                    "timeout": "5s",
                    "threshold": 3,
                    "tcp": {
                        "port": LIVEBLOCKS_PORT,
                    },
                },
            },
        })

    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        """Handle pebble-ready event."""
        container = event.workload
        if not container.can_connect():
            self.unit.status = ops.WaitingStatus("Waiting for Pebble")
            return

        container.add_layer("liveblocks", self._get_pebble_layer(), combine=True)
        container.replan()

        logger.info("Liveblocks dev server started on port %d", LIVEBLOCKS_PORT)
        self.unit.status = ops.ActiveStatus()

    def _on_config_changed(self, event: ops.ConfigChangedEvent) -> None:
        """Handle config-changed event."""
        container = self.unit.get_container("liveblocks")
        if not container.can_connect():
            self.unit.status = ops.WaitingStatus("Waiting for Pebble")
            return

        container.add_layer("liveblocks", self._get_pebble_layer(), combine=True)
        container.replan()

        self.unit.status = ops.ActiveStatus()

    def _on_update_status(self, event: ops.UpdateStatusEvent) -> None:
        """Handle update-status event for periodic health checking."""
        container = self.unit.get_container("liveblocks")
        if not container.can_connect():
            self.unit.status = ops.WaitingStatus("Waiting for Pebble")
            return

        try:
            service = container.get_service("liveblocks")
            if service.is_running():
                self.unit.status = ops.ActiveStatus()
            else:
                self.unit.status = ops.BlockedStatus("Service not running")
        except ops.pebble.APIError:
            self.unit.status = ops.WaitingStatus("Waiting for service")

    def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
        """Handle pebble-check-failed event."""
        logger.warning("Health check '%s' failed", event.info.name)
        self.unit.status = ops.BlockedStatus(f"Health check failed: {event.info.name}")

    def _on_pebble_check_recovered(self, event: ops.PebbleCheckRecoveredEvent) -> None:
        """Handle pebble-check-recovered event."""
        logger.info("Health check '%s' recovered", event.info.name)
        self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":
    ops.main(LiveblocksDevServerCharm)

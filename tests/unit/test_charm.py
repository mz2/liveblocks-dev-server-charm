"""Unit tests for Liveblocks Dev Server charm."""

import unittest

import ops
import ops.testing

from charm import LiveblocksDevServerCharm


class TestCharm(unittest.TestCase):
    """Test cases for LiveblocksDevServerCharm."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.harness = ops.testing.Harness(LiveblocksDevServerCharm)
        self.addCleanup(self.harness.cleanup)

    def test_pebble_ready_sets_active_status(self) -> None:
        """Test that pebble-ready event sets charm to active status."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        self.assertIsInstance(self.harness.model.unit.status, ops.ActiveStatus)

    def test_initial_status_is_maintenance(self) -> None:
        """Test that initial charm status is maintenance before hooks run."""
        self.harness.begin()
        self.assertIsInstance(self.harness.model.unit.status, ops.MaintenanceStatus)

    def test_pebble_layer_added_on_ready(self) -> None:
        """Test that Pebble layer is added when pebble becomes ready."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        plan = self.harness.get_container_pebble_plan("liveblocks")
        self.assertIn("liveblocks", plan.services)

    def test_config_changed_updates_layer(self) -> None:
        """Test that config-changed event updates the Pebble layer."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        self.harness.update_config({"external-hostname": "test.local"})
        self.assertIsInstance(self.harness.model.unit.status, ops.ActiveStatus)

    def test_config_changed_without_pebble_waits(self) -> None:
        """Test that config-changed without Pebble sets waiting status."""
        self.harness.begin()
        self.harness.update_config({"external-hostname": "test.local"})
        self.assertIsInstance(self.harness.model.unit.status, ops.WaitingStatus)

    def test_ingress_relation_initialized(self) -> None:
        """Test that ingress relation is initialized."""
        self.harness.begin()
        self.assertTrue(hasattr(self.harness.charm, "ingress"))

    def test_ingress_uses_external_hostname_config(self) -> None:
        """Test that ingress uses external-hostname from config."""
        self.harness.begin_with_initial_hooks()
        self.harness.update_config({"external-hostname": "custom.example.com"})
        hostname = self.harness.charm._get_ingress_hostname()
        self.assertEqual(hostname, "custom.example.com")

    def test_ingress_uses_app_name_when_no_hostname(self) -> None:
        """Test that ingress uses app name when external-hostname is empty."""
        self.harness.begin_with_initial_hooks()
        hostname = self.harness.charm._get_ingress_hostname()
        self.assertEqual(hostname, self.harness.charm.app.name)

    def test_pebble_layer_has_health_checks(self) -> None:
        """Test that Pebble layer includes health checks."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        plan = self.harness.get_container_pebble_plan("liveblocks")
        self.assertIn("checks", plan.to_dict())

    def test_update_status_checks_service(self) -> None:
        """Test that update_status event checks service health."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        self.harness.charm.on.update_status.emit()
        # After update_status with running service, should be active
        self.assertIsInstance(self.harness.model.unit.status, ops.ActiveStatus)


if __name__ == "__main__":
    unittest.main()

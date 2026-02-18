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

    def test_config_changed_maintains_active_status(self) -> None:
        """Test that config-changed event maintains active status."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        self.harness.charm.on.config_changed.emit()
        self.assertIsInstance(self.harness.model.unit.status, ops.ActiveStatus)

    def test_config_changed_without_pebble_waits(self) -> None:
        """Test that config-changed without Pebble sets waiting status."""
        self.harness.begin()
        self.harness.charm.on.config_changed.emit()
        self.assertIsInstance(self.harness.model.unit.status, ops.WaitingStatus)

    def test_ingress_relation_initialized(self) -> None:
        """Test that ingress relation is initialized."""
        self.harness.begin()
        self.assertTrue(hasattr(self.harness.charm, "ingress"))

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

    def test_pebble_layer_service_config(self) -> None:
        """Test that Pebble layer has correct service configuration."""
        self.harness.begin_with_initial_hooks()
        container = self.harness.model.unit.get_container("liveblocks")
        self.harness.charm.on["liveblocks"].pebble_ready.emit(container)
        plan = self.harness.get_container_pebble_plan("liveblocks")
        service = plan.services["liveblocks"]
        self.assertEqual(service.startup, "enabled")
        self.assertIn("1153", service.command)


if __name__ == "__main__":
    unittest.main()

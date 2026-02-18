"""Integration tests for Liveblocks Dev Server charm."""

import asyncio
import logging

import pytest
import requests
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

CHARM_NAME = "liveblocks-dev-server"
LIVEBLOCKS_PORT = 1153


async def get_unit_address(ops_test: OpsTest) -> str:
    """Get the unit address using juju show-unit."""
    unit_name = f"{CHARM_NAME}/0"
    raw_data = await ops_test.juju("show-unit", unit_name)
    if not raw_data:
        raise ValueError(f"No data returned from show-unit for {unit_name}")

    import yaml
    unit_data = yaml.safe_load(raw_data[1])
    address = unit_data[unit_name].get("address")
    if not address:
        raise ValueError(f"No address found for unit {unit_name}")
    return address


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test: OpsTest):
    """Build the charm and deploy it."""
    charm = await ops_test.build_charm(".")

    await ops_test.model.deploy(
        charm,
        application_name=CHARM_NAME,
        resources={"liveblocks-image": "ghcr.io/liveblocks/dev-server:latest"},
    )

    await ops_test.model.wait_for_idle(
        apps=[CHARM_NAME],
        status="active",
        timeout=300,
    )


async def test_charm_is_active(ops_test: OpsTest):
    """Test that the charm reaches active status."""
    assert ops_test.model.applications[CHARM_NAME].status == "active"


async def test_unit_is_active(ops_test: OpsTest):
    """Test that the unit reaches active status."""
    unit = ops_test.model.applications[CHARM_NAME].units[0]
    assert unit.workload_status == "active"


async def test_liveblocks_api_health(ops_test: OpsTest):
    """Test that the Liveblocks API is responding."""
    unit_ip = await get_unit_address(ops_test)

    # Wait a moment for the service to be fully ready
    await asyncio.sleep(5)

    # Test the rooms API endpoint
    url = f"http://{unit_ip}:{LIVEBLOCKS_PORT}/v2/rooms"
    headers = {"Authorization": "Bearer sk_localdev"}

    response = requests.get(url, headers=headers, timeout=10)
    assert response.status_code == 200

    # Response should be JSON with a data field
    data = response.json()
    assert "data" in data


async def test_create_room(ops_test: OpsTest):
    """Test creating a room via the Liveblocks API."""
    unit_ip = await get_unit_address(ops_test)

    url = f"http://{unit_ip}:{LIVEBLOCKS_PORT}/v2/rooms"
    headers = {
        "Authorization": "Bearer sk_localdev",
        "Content-Type": "application/json",
    }
    payload = {"id": "integration-test-room"}

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert data["type"] == "room"
    assert data["id"] == "integration-test-room"


async def test_list_rooms_includes_created_room(ops_test: OpsTest):
    """Test that listing rooms includes the room we created."""
    unit_ip = await get_unit_address(ops_test)

    url = f"http://{unit_ip}:{LIVEBLOCKS_PORT}/v2/rooms"
    headers = {"Authorization": "Bearer sk_localdev"}

    response = requests.get(url, headers=headers, timeout=10)
    assert response.status_code == 200

    data = response.json()
    room_ids = [room["id"] for room in data.get("data", [])]
    assert "integration-test-room" in room_ids


async def test_get_specific_room(ops_test: OpsTest):
    """Test getting a specific room by ID."""
    unit_ip = await get_unit_address(ops_test)

    url = f"http://{unit_ip}:{LIVEBLOCKS_PORT}/v2/rooms/integration-test-room"
    headers = {"Authorization": "Bearer sk_localdev"}

    response = requests.get(url, headers=headers, timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert data["type"] == "room"
    assert data["id"] == "integration-test-room"


async def test_delete_room(ops_test: OpsTest):
    """Test deleting a room via the API."""
    unit_ip = await get_unit_address(ops_test)

    url = f"http://{unit_ip}:{LIVEBLOCKS_PORT}/v2/rooms/integration-test-room"
    headers = {"Authorization": "Bearer sk_localdev"}

    response = requests.delete(url, headers=headers, timeout=10)
    assert response.status_code == 204 or response.status_code == 200

    # Verify the room is deleted
    response = requests.get(url, headers=headers, timeout=10)
    assert response.status_code == 404

import pytest


@pytest.mark.asyncio
async def test_get_sensor(mock_redis):
    """
    Test fetching sensor details from Redis.
    """
    result = await mock_redis.get_sensor("AA:BB:CC:DD:EE:FF")
    assert result == {"device_type": "access_controller"}


@pytest.mark.asyncio
async def test_is_authorized_user(mock_redis):
    """
    Test checking if a user is authorized.
    """
    result = await mock_redis.is_authorized_user("authorized_user")
    assert result is True


@pytest.mark.asyncio
async def test_add_sensor(mock_redis):
    """
    Test adding a sensor to Redis.
    """
    await mock_redis.add_sensor("11:22:33:44:55:66", {"device_type": "radar"})
    mock_redis.add_sensor.assert_called_with("11:22:33:44:55:66", {"device_type": "radar"})

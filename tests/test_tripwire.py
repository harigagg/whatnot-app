import pytest
from unittest.mock import patch
from services.tripwire import track_tripwire, update_tripwire_count, check_tripwire, enable_restriction, is_restriction_active
import time

@pytest.fixture
def mock_redis():
    """Mock Redis instance."""
    with patch("app.redis") as mock_redis:
        yield mock_redis


def test_track_tripwire(mock_redis):
    event_type = "message_restriction"
    user_id = "123"
    current_time = int(time.time())
    key = f"tripwire:{event_type}:{current_time // 300}"

    track_tripwire(event_type, user_id)

    mock_redis.sadd.assert_called_with(key, user_id)
    mock_redis.expire.assert_called_with(key, 360)


def test_update_tripwire_count(mock_redis):
    event_type = "purchase_restriction"
    user_id = "456"

    with patch("services.tripwire.track_tripwire") as mock_track:
        update_tripwire_count(event_type, user_id)
        mock_track.assert_called_with(event_type, user_id)


def test_check_tripwire(mock_redis):
    event_type = "message_restriction"
    total_user_count = 100

    # Mocking smembers to return specific sets for the first few calls
    def smembers_side_effect(*args, **kwargs):
        responses = [
            {"user1", "user2"},  # First window
            {"user3"},           # Second window
            set(),               # Third window
            set(),               # Fourth window
            set(),               # Fifth window
        ]
        if len(responses) > 0:
            return responses.pop(0)
        return set()  # Return empty set if more calls are made

    mock_redis.smembers.side_effect = smembers_side_effect

    result = check_tripwire(event_type, total_user_count)

    # Verify the results
    assert not result  # Tripwire should not be triggered
    assert mock_redis.smembers.call_count == 5  # Ensure smembers was called 5 times



def test_enable_restriction(mock_redis):
    event_type = "purchase_restriction"
    enable_restriction(event_type)
    mock_redis.set.assert_called_with(
        f"restriction_enabled:{event_type}", "true", ex=3600)


def test_is_restriction_active(mock_redis):
    event_type = "message_restriction"
    mock_redis.get.return_value = None  # Simulates an active restriction

    assert is_restriction_active(event_type)
    mock_redis.get.assert_called_with(f"restriction_enabled:{event_type}")

import time
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Constants for tripwire logic
TRIPWIRE_THRESHOLD = 0.05  # 5% of the user base
TRIPWIRE_WINDOW = 300      # 5 minutes in seconds


def track_tripwire(event_type, user_id):
    """
    Tracks the number of users impacted by a specific restriction type.
    
    Parameters:
        event_type (str): The type of restriction ("message_restriction" or "purchase_restriction").
        user_id (str): The ID of the affected user.
    """
    from app import redis
    current_time = int(time.time())
    key = f"tripwire:{event_type}:{current_time // TRIPWIRE_WINDOW}"
    redis.sadd(key, user_id)
    # expire keys a bit after the window
    redis.expire(key, TRIPWIRE_WINDOW + 60)


def update_tripwire_count(event_type, user_id):
    """
    Updates the count of affected users for a specific restriction type.

    Parameters:
        event_type (str): The restriction type to track (e.g., "message_restriction" or "purchase_restriction").
        user_id (str): The ID of the affected user.
    """
    from app import redis
    # Track the event by adding the user to Redis
    track_tripwire(event_type, user_id)


def check_tripwire(event_type, total_user_count):
    """
    Checks if the tripwire threshold has been exceeded for a restriction type.
    
    Parameters:
        event_type (str): The restriction type to check (e.g., "message_restriction" or "purchase_restriction").
        total_user_count (int): The total number of active users.

    Returns:
        bool: True if the restriction should be deactivated, False otherwise.
    """
    from app import redis
    # Calculate the total number of unique affected users within the time window
    affected_users = set()
    current_time = int(time.time())
    for window_offset in range(5):
        key = f"tripwire:{event_type}:{(current_time - window_offset * 60) // TRIPWIRE_WINDOW}"
        affected_users.update(redis.smembers(key))

    affected_user_count = len(affected_users)
    impact_ratio = affected_user_count / total_user_count
    log.debug(TRIPWIRE_THRESHOLD, impact_ratio)
    log.debug("Affected users:", affected_user_count)
    if impact_ratio > TRIPWIRE_THRESHOLD and total_user_count > 5:
        # Enable restriction if more than 5% of users are affected
        enable_restriction(event_type)
        return True
    return False


def enable_restriction(event_type):
    """
    enables a specific restriction type by updating the Redis cache.

    Parameters:
        event_type (str): The restriction type to disable (e.g., "message_restriction" or "purchase_restriction").
    """
    from app import redis
    redis.set(f"restriction_enabled:{event_type}",
              "true", ex=3600)  # enable for 1 hour
    log.info(f"Tripwire activated: {event_type} has been enabled.")


def is_restriction_active(event_type):
    """
    Checks if a restriction is currently active.

    Parameters:
        event_type (str): The restriction type to check (e.g., "message_restriction" or "purchase_restriction").

    Returns:
        bool: False if the restriction is disabled, True otherwise.
    """
    from app import redis
    return redis.get(f"restriction_enabled:{event_type}") is None

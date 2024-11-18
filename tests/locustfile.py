from locust import HttpUser, task, between
import random
import threading

# Shared storage for user IDs (thread-safe)
user_ids = []
user_ids_lock = threading.Lock()

event_prop = {   
    "event_properties_add_credit_card": {
        "user_id": str(random.randint(1, 1000)),
        "total_spend": random.randint(100, 1000),
        "card_id": 378282246310002,
        "last_four_digits": str(random.randint(1000, 9999)),
        "zip_code": str(random.randint(10000, 99999)),
    },
    "event_properties_flag_scam_message": {
    "user_id": str(random.randint(1, 1000)),
    },
    "event_properties_chargeback": {
        "user_id": str(random.randint(1, 1000)),
        "chargebacks": random.randint(0, 100),
    }
}

class EventIngestionUser(HttpUser):
    # Simulate a user sending events every 1-2 seconds
    wait_time = between(1, 2)

    @task
    def send_event(self):
        event_data = {
            "name": random.choice(["add_credit_card", "flag_scam_message", "chargeback"]),
        }
        if event_data["name"] == "add_credit_card":
            event_data["event_properties"] = event_prop["event_properties_add_credit_card"]
        elif event_data["name"] == "flag_scam_message":
            event_data["event_properties"] = event_prop["event_properties_flag_scam_message"]
        elif event_data["name"] == "chargeback":
            event_data["event_properties"] = event_prop["event_properties_chargeback"]
        response = self.client.post("/event", json=event_data)
        if response.status_code == 200:
            with user_ids_lock:
                user_ids.append(event_data["event_properties"]["user_id"])


class FeatureRestrictionUser(HttpUser):
    # Simulate a user querying feature restrictions every 1-2 seconds
    wait_time = between(1, 2)

    @task
    def get_restriction(self):
        # Pick a random user_id from the shared storage
        with user_ids_lock:
            if user_ids:
                user_id = random.choice(user_ids)
            else:
                return  # No user IDs available yet
            
        feature = random.choice(
            ["canmessage", "canpurchase"])
        self.client.get(f"/{feature}?user_id={user_id}")

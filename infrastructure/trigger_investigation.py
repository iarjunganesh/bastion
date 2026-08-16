"""Publishes a Pub/Sub message to kick off an investigation locally,
for the 1:10-1:40 demo beat."""

import json
import os

from google.cloud import pubsub_v1

from runtime.events import new_investigation_payload

project_id = os.environ["GCP_PROJECT_ID"]
topic = os.environ.get("PUBSUB_TOPIC", "bastion-investigations")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic)

payload = new_investigation_payload()
message_id = publisher.publish(
    topic_path, json.dumps(payload, sort_keys=True).encode("utf-8")
).result()
print(
    f"Published investigation {payload['event_id']} as Pub/Sub message {message_id} to {topic_path}"
)

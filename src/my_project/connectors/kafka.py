import json

from kafka import KafkaProducer


def producer(server: str = "localhost:9092"):
    return KafkaProducer(
        bootstrap_servers=server,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

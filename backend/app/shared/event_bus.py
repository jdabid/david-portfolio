"""
Event Bus — publishes domain events to RabbitMQ.
Uses aio_pika for async AMQP communication.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    event_type: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


async def publish_event(event: DomainEvent, routing_key: str) -> None:
    """Publish an event to RabbitMQ exchange."""
    try:
        import aio_pika

        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "portfolio.events", aio_pika.ExchangeType.TOPIC, durable=True
            )
            message = aio_pika.Message(
                body=json.dumps(asdict(event)).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key=routing_key)
            logger.info(f"Published event: {routing_key}")
    except Exception as e:
        logger.warning(f"Failed to publish event {routing_key}: {e}")

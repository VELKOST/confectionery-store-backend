import os
import pika
import json

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")


def publish_payment_status(payment_data: dict):
    # payment_data: {"payment_id": ..., "order_id": ..., "status": ..., "amount": ...}
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="payments_queue", durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='payments_queue',
        body=json.dumps(payment_data),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()

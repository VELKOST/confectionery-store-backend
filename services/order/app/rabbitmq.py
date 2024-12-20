import os
import pika
import json

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")


def publish_order_created(order_data: dict):
    # order_data - словарь с информацией о заказе
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="orders_queue", durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='orders_queue',
        body=json.dumps(order_data),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()

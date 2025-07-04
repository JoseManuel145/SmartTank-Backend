import pika
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class RabbitConsumer:
    def __init__(self, host=None, exchange=None, binding_keys=None):
        self.host = host or os.getenv("RABBIT_HOST")
        self.exchange = exchange or os.getenv("RABBIT_EXCHANGE")
        self.binding_keys = binding_keys or os.getenv("RABBIT_BINDING_KEYS").split(",")
        self.connection = None
        self.channel = None
        self.queue_name = None
        credentials = pika.PlainCredentials(os.getenv("RABBIT_USER"), os.getenv("RABBIT_PASSWORD")) 

        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=5672, credentials=credentials))
        except Exception as e:
            print(f"[RabbitMQ] Error al conectar con RabbitMQ en {self.host}: {e}")
            raise

        try:
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic', durable=True)
        except Exception as e:
            print(f"[RabbitMQ] Error al declarar el exchange '{self.exchange}': {e}")
            self.close()
            raise

        try:
            result = self.channel.queue_declare('', exclusive=True)
            self.queue_name = result.method.queue
            for binding_key in self.binding_keys:
                self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=binding_key)
        except Exception as e:
            print(f"[RabbitMQ] Error al declarar o enlazar la cola: {e}")
            self.close()
            raise

    def start_consuming(self, callback):
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            print(' [*] Waiting for messages. To exit press CTRL+C')
            self.channel.start_consuming()
        except Exception as e:
            print(f"[RabbitMQ] Error durante el consumo de mensajes: {e}")
            self.close()
            raise

    def close(self):
        if self.connection and self.connection.is_open:
            try:
                self.channel.close()
            except Exception as e:
                print(f"[RabbitMQ] Error al cerrar el canal: {e}")
            try:
                self.connection.close()
            except Exception as e:
                print(f"[RabbitMQ] Error al cerrar la conexión: {e}")

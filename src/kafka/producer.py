from time import sleep
from datetime import datetime
from pathlib import Path

import click
from loguru import logger
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from api_data import CryptoRecord, CryptoRecordKey, request_data_for_symbol, format_api_output_for_symbol
from settings import KEY_SCHEMA_PATH, VALUE_SCHEMA_PATH, SCHEMA_REGISTRY_URL, BOOTSTRAP_SERVERS, KAFKA_TOPIC


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def delivery_report(err, msg):
    if err is not None:
        logger.error(f'Delivery failed for record {msg.key()}: {err}')
        return
    logger.debug(f'Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


class CryptoAvroProducer:
    def __init__(self, props: dict):
        schema_registry_props = {'url': props['schema_registry.url']}
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.key_serializer = AvroSerializer(
            schema_registry_client=schema_registry_client,
            schema_str=self.load_schema(props['schema.key']),
            to_dict=lambda record_key, *args, **kwargs: record_key.__dict__
        )
        self.value_serializer = AvroSerializer(
            schema_registry_client=schema_registry_client,
            schema_str=self.load_schema(props['schema.value']),
            to_dict=lambda record, *args, **kwargs: record.__dict__
        )
        producer_props = {'bootstrap.servers': props['bootstrap.servers']}
        self.producer = Producer(producer_props)

    @staticmethod
    def load_schema(schema_path: str) -> str:
        with open(Path(__file__).resolve().parent / schema_path) as f:
            return f.read()

    @staticmethod
    def request_data(api_key: str, symbols: list[str], resolution: str,
                     datetime_start: datetime, datetime_end: datetime) -> [CryptoRecordKey, CryptoRecord]:
        for symbol in symbols:
            api_output = request_data_for_symbol(api_key, symbol, resolution, datetime_start, datetime_end)
            records = format_api_output_for_symbol(symbol, resolution, api_output)
            for record in records:
                key = CryptoRecordKey(symbol=record.symbol, date=record.date_string)
                yield key, record

    def publish(self, topic: str, records: [CryptoRecordKey, CryptoRecord]):
        for key, value in records:
            try:
                self.producer.produce(
                    topic=topic,
                    key=self.key_serializer(key, SerializationContext(topic=topic, field=MessageField.KEY)),
                    value=self.value_serializer(value, SerializationContext(topic=topic, field=MessageField.VALUE)),
                    on_delivery=delivery_report
                )
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Exception while producing record - {value}: {e}")

        self.producer.flush()
        sleep(1)


@click.command()
@click.option('--api-key', '-k', type=click.STRING, required=True, help='finnhub.io API key')
@click.option('--host', '-h', type=click.STRING, required=False, default='localhost')
@click.option('--symbols', '-c', type=click.STRING, required=True, multiple=True)
@click.option('--resolution', '-r', type=click.STRING, required=False, default='60')
@click.option('--datetime-start', '-s', type=click.DateTime(formats=['%Y-%m-%dT%H:%M:%S']), required=False,
              default=datetime.now().replace(hour=0, minute=0, second=0).strftime(DATETIME_FORMAT))
@click.option('--datetime-end', '-e', type=click.DateTime(formats=['%Y-%m-%dT%H:%M:%S']), required=False,
              default=datetime.now().replace(hour=23, minute=59, second=59).strftime(DATETIME_FORMAT))
def cli(**kwargs):
    """
    Collect data from API to Kafka.
    Resolutions:
        1, 5, 15, 30, 60, D, W, M
    Symbols examples:
        BINANCE:ETHUSDT, BINANCE:BTCUSDT, BINANCE:DOGEUSDT, BINANCE:XRPUSDT
    Usage example:
        python producer.py -k $API_KEY -c BINANCE:ETHUSDT -c BINANCE:BTCUSDT -c BINANCE:DOGEUSDT -c BINANCE:XRPUSDT -s 2023-03-01 -e 2023-03-04
    """
    host = kwargs.pop('host')
    config = {
        'bootstrap.servers': BOOTSTRAP_SERVERS.format(host=host),
        'schema_registry.url': SCHEMA_REGISTRY_URL.format(host=host),
        'schema.key': KEY_SCHEMA_PATH,
        'schema.value': VALUE_SCHEMA_PATH
    }
    producer = CryptoAvroProducer(props=config)
    crypto_records = producer.request_data(**kwargs)
    producer.publish(topic=KAFKA_TOPIC, records=crypto_records)


if __name__ == '__main__':
    cli()

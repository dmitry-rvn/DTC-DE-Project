"""
TODO: write to GSC bucket
"""
from pathlib import Path

import click
from loguru import logger
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from api_data import CryptoRecordKey, CryptoRecord
from settings import BOOTSTRAP_SERVERS, SCHEMA_REGISTRY_URL, KEY_SCHEMA_PATH, VALUE_SCHEMA_PATH, KAFKA_TOPIC
from writer import write_avro


class CryptoAvroConsumer:
    def __init__(self, props: dict):
        schema_registry_props = {'url': props['schema_registry.url']}
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.avro_key_deserializer = AvroDeserializer(
            schema_registry_client=schema_registry_client,
            schema_str=self.load_schema(props['schema.key']),
            from_dict=lambda dct, *args, **kwargs: CryptoRecordKey.from_dict(dct) if dct else None
        )
        self.avro_value_deserializer = AvroDeserializer(
            schema_registry_client=schema_registry_client,
            schema_str=self.load_schema(props['schema.value']),
            from_dict=lambda dct, *args, **kwargs: CryptoRecord.from_dict(dct) if dct else None
        )
        consumer_props = {
            'bootstrap.servers': props['bootstrap.servers'],
            'group.id': props['group.id'],
            'auto.offset.reset': props['auto.offset.reset']
        }
        self.consumer = Consumer(consumer_props)

    @staticmethod
    def load_schema(schema_path: str) -> str:
        with open(Path(__file__).resolve().parent / schema_path) as f:
            return f.read()

    def consume_from_kafka(self, topics: list[str], bucket_name: str):
        self.consumer.subscribe(topics=topics)
        while True:
            try:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                key = self.avro_key_deserializer(msg.key(), SerializationContext(msg.topic(), MessageField.KEY))
                record = self.avro_value_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                if record is not None:
                    logger.debug(f'{key = }, {record = }')

                    dt = key.date
                    symbol = key.symbol.replace(':', '-')

                    filepath = Path(f"data/{dt}/{symbol}-{dt}.avro")
                    logger.debug(f'{filepath = }')
                    if not filepath.exists():
                        filepath.resolve().parent.mkdir(parents=True, exist_ok=True)
                        # with open(filepath, 'w') as f:
                        #     f.write('')
                    # with open(filepath, 'a') as f:
                        # f.write(json.dumps(record.__dict__) + '\n')
                    write_avro(record, filepath)

                    # write_to_gcs(bucket_name, f'data.jsonlines', json.dumps(record.__dict__))
            except KeyboardInterrupt:
                break

        self.consumer.close()


@click.command()
@click.option('--host', '-h', type=click.STRING, required=False, default='localhost')
@click.option('--group-id', '-g', type=click.STRING, required=False, default='dshol.crypto.avro.consumer.1')
@click.option('--auto-offset-reset', '-f', type=click.STRING, required=False, default='earliest')
@click.option('--bucket-name', '-b', type=click.STRING, required=False, default='dshol-crypto-data')
def cli(host: str, group_id: str, auto_offset_reset: str, bucket_name: str):
    config = {
        'bootstrap.servers': BOOTSTRAP_SERVERS.format(host=host),
        'group.id': group_id,
        'auto.offset.reset': auto_offset_reset,
        'schema_registry.url': SCHEMA_REGISTRY_URL.format(host=host),
        'schema.key': KEY_SCHEMA_PATH,
        'schema.value': VALUE_SCHEMA_PATH,
    }
    avro_consumer = CryptoAvroConsumer(props=config)
    avro_consumer.consume_from_kafka(topics=[KAFKA_TOPIC], bucket_name=bucket_name)


if __name__ == '__main__':
    cli()

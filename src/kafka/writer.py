import json

from fastavro import parse_schema, writer, reader


with open('schemas/crypto_record_value.avsc') as f:
    schema = parse_schema(json.load(f))
    # schema = f.read()


def write_avro(record, filepath):
    with open(filepath, 'a+b') as f:
        writer(f, schema, [record.__dict__])


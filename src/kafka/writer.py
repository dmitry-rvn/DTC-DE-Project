import json
from pathlib import Path

from fastavro import parse_schema, writer

from settings import VALUE_SCHEMA_PATH


with open(Path(__file__).resolve().parent / VALUE_SCHEMA_PATH) as f:
    schema = parse_schema(json.load(f))


def write_avro(record, filepath):
    with open(filepath, 'a+b') as f:
        writer(f, schema, [record.__dict__])


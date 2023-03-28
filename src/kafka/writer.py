import json
from pathlib import Path

from fastavro import parse_schema, writer

from api_data import CryptoRecord
from settings import VALUE_SCHEMA_PATH


with open(Path(__file__).resolve().parent / VALUE_SCHEMA_PATH) as f:
    SCHEMA = parse_schema(json.load(f))


def write_avro(record: CryptoRecord, filepath: Path):
    with open(filepath, 'a+b') as avro_file:
        writer(avro_file, SCHEMA, [record.__dict__])

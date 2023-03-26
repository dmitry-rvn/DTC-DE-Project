from pathlib import Path

import click
from google.cloud import storage
from loguru import logger


@click.command()
@click.option('--credentials-file', type=click.Path(exists=True, file_okay=True), required=True)
@click.option('--input-dir', type=click.Path(exists=True, dir_okay=True, file_okay=False), required=True)
@click.option('--bucket-name', type=click.STRING, required=True)
@click.option('--storage-dir', type=click.STRING, required=True)
def cli(credentials_file: str, input_dir: str, bucket_name: str, storage_dir: str):
    """
    Load local data (from `input_dir`) to Google Cloud Storage (to bucket `bucket_name` and folder `storage_dir`).
    Local data must be placed like:
        input_dir
            dt=YYYY-MM-DD
                file1.avro
                file2.avro
                ...
                fileN.avro
            dt=YYYY-MM-DD
                file1.avro
                ...
                fileN.avro
    where `dt=YYYY-MM-DD` - folders (= partitions by day).
    """
    storage_client = storage.Client.from_service_account_json(credentials_file)
    bucket = storage_client.get_bucket(bucket_name)

    for partition_dir in Path(input_dir).glob('dt=*'):
        logger.info(f'Processing: {partition_dir}')
        for file in partition_dir.glob('*'):
            storage_filepath = f'{storage_dir}/{partition_dir.name}/{file.name}'
            logger.info(f'Copying {file} to {storage_filepath}')
            blob = bucket.blob(storage_filepath)
            blob.upload_from_filename(file)


if __name__ == '__main__':
    cli()

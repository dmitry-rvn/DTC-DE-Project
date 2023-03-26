/*
dtc_crypto_data -- BigQuery dataset name
dshol-dtc-data -- Google Cloud Storage bucket name
*/
CREATE OR REPLACE EXTERNAL TABLE dtc_crypto_data.ext_trade_data
WITH PARTITION COLUMNS
OPTIONS (
  format = 'AVRO',
  hive_partition_uri_prefix = "gs://dshol-dtc-data/trade_data",
  uris = ['gs://dshol-dtc-data/trade_data/*.avro']
)


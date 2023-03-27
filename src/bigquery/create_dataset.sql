/*
CREATE DATASET

dshol-dtc-de -- Project ID
dtc_crypto_data -- BigQuery dataset name
*/
CREATE SCHEMA `dshol-dtc-de`.dtc_crypto_data
    OPTIONS (
        description = 'Dataset for DTC DE Zoomcamp project',
        location = 'EU'
    );
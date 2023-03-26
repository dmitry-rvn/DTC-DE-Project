{{ config(materialized='table') }}

SELECT DISTINCT
    symbol,
    dt,
    TIMESTAMP_SECONDS(timestamp) AS date_time,
    volume,
    close_price AS price_close,
    open_price AS price_open,
    close_price - open_price AS price_delta
FROM {{ source('core', 'ext_trade_data') }}
WHERE resolution = '60'

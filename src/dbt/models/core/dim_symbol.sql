{{ config(materialized='table') }}

SELECT
    symbol,
    display_symbol,
    description,
    exchange
FROM {{ ref('symbols') }}

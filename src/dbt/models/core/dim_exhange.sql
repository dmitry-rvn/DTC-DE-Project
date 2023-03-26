{{ config(materialized='table') }}

SELECT
    exchange_id,
    exchange_name,
    company_name
FROM {{ ref('exchanges') }}
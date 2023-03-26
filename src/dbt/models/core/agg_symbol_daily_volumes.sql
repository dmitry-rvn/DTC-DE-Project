{{ config(materialized='table') }}

SELECT
    s.exchange,
    s.symbol,
    s.description AS symbol_description,
    t.dt,
    SUM(t.volume) AS volume
FROM {{ ref('fct_trade_data_hourly') }} t
JOIN {{ ref('dim_symbol') }} s ON s.symbol = t.symbol
GROUP BY 1, 2, 3, 4

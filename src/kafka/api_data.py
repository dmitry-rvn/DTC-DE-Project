"""
API reference: https://finnhub.io/docs/api/crypto-candles
"""
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any

import finnhub
from loguru import logger
import click


# RESOLUTION = '60'  # 60 minutes; available values: 1, 5, 15, 30, 60, D, W, M
# SYMBOLS = ['BINANCE:ETHUSDT', 'BINANCE:BTCUSDT', 'BINANCE:DOGEUSDT', 'BINANCE:XRPUSDT']


@dataclass
class CryptoRecordKey:
    symbol: str
    date: str

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)


@dataclass
class CryptoRecord:
    symbol: str
    resolution: str
    close_price: float
    open_price: float
    volume: float
    timestamp: int

    @property
    def date_string(self) -> str:
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)


def format_api_output_for_symbol(symbol: str, resolution: str, api_output: dict[str, list[Any]]) -> list[CryptoRecord]:
    records = []
    if api_output.get('s') != 'ok':
        logger.warning(f'Status not OK for {symbol = }, {resolution = }')
        return []

    for c, o, v, t in zip(api_output['c'], api_output['o'], api_output['v'], api_output['t']):
        records.append(CryptoRecord(symbol, resolution, c, o, v, t))

    logger.debug(f'Got {len(records)} records for {symbol = }, {resolution = }')
    return records


def request_data_for_symbol(api_key: str, symbol: str, resolution: str,
                            datetime_start: datetime, datetime_end: datetime) -> dict[str, list[Any]]:
    logger.debug(f'Data request: {symbol = }, {resolution = }, {datetime_start = }, {datetime_end = }')
    finnhub_client = finnhub.Client(api_key=api_key)
    dt_start_ts = int(datetime_start.timestamp())
    dt_end_ts = int(datetime_end.timestamp())
    api_output = finnhub_client.crypto_candles(symbol=symbol, resolution=resolution, _from=dt_start_ts, to=dt_end_ts)
    return api_output

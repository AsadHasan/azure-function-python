"""Return dividends history of required stock (Ticker)."""
import json
from typing import Dict, Optional

import yfinance as yf
from azure.functions import HttpRequest
from pandas import DataFrame
from yfinance import Ticker


def _get_ticker(ticker_name: str) -> Ticker:
    return yf.Ticker(ticker_name)


def _get_ticker_history(ticker: Ticker) -> DataFrame:
    return ticker.history()


def _get_pretty_json_string(obj: object) -> str:
    return json.dumps(obj, indent=4)


def _get_dividends_history(ticker_history: DataFrame) -> Optional[str]:
    if not ticker_history.empty:
        history_json: str = ticker_history.to_json(date_format="iso")
        history_dict: Dict[str, Dict[str, str]] = json.loads(history_json)
        dividends: Dict[str, Dict[str, str]] = {
            k: v for (k, v) in history_dict.items() if k == "Dividends"
        }
        return _get_pretty_json_string(dividends)
    return None


def main(req: HttpRequest) -> str:
    """Azure function to get stock's dividend history from Yahoo finance

    Args:
        request (HttpRequest): GET request containing Ticker (stock) name
    """
    ticker_name: Optional[str] = req.route_params.get("ticker")
    if ticker_name:
        ticker: Ticker = _get_ticker(ticker_name)
        history: DataFrame = _get_ticker_history(ticker)
        dividends: Optional[str] = _get_dividends_history(history)
        return dividends or _get_pretty_json_string(
            {
                "error": f"Couldn't find dividends for {ticker_name}, is {ticker_name} valid?"
            }
        )
    return "No ticker name provided"

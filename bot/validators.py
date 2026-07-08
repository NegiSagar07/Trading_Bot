"""Input validation helpers for the trading bot CLI."""

from __future__ import annotations

import re
from typing import Literal, Optional

Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]

_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,20}$")


def validate_symbol(symbol: str) -> str:
    """Validate and normalize a Binance trading symbol."""
    if not isinstance(symbol, str):
        raise ValueError("symbol must be a string.")

    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required.")
    if not _SYMBOL_PATTERN.fullmatch(normalized):
        raise ValueError("symbol must contain only uppercase letters and digits.")
    return normalized


def validate_side(side: str) -> Side:
    """Validate the order side."""
    if not isinstance(side, str):
        raise ValueError("side must be a string.")

    normalized = side.strip().upper()
    if normalized not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL.")
    return normalized  # type: ignore[return-value]


def validate_order_type(order_type: str) -> OrderType:
    """Validate the order type."""
    if not isinstance(order_type, str):
        raise ValueError("type must be a string.")

    normalized = order_type.strip().upper()
    if normalized not in {"MARKET", "LIMIT"}:
        raise ValueError("type must be MARKET or LIMIT.")
    return normalized  # type: ignore[return-value]


def validate_quantity(quantity: float) -> float:
    """Validate the order quantity."""
    try:
        value = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError("quantity must be a positive number.") from exc

    if value <= 0:
        raise ValueError("quantity must be a positive number.")
    return value


def validate_price(order_type: str, price: Optional[float]) -> Optional[float]:
    """Validate the limit price when required."""
    normalized_type = validate_order_type(order_type)

    if normalized_type == "MARKET":
        if price is not None:
            raise ValueError("price is only allowed for LIMIT orders.")
        return None

    if price is None:
        raise ValueError("price is required for LIMIT orders.")

    try:
        value = float(price)
    except (TypeError, ValueError) as exc:
        raise ValueError("price must be a positive number.") from exc

    if value <= 0:
        raise ValueError("price must be a positive number.")
    return value


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> dict[str, object]:
    """Validate and normalize all order inputs."""
    normalized_symbol = validate_symbol(symbol)
    normalized_side = validate_side(side)
    normalized_type = validate_order_type(order_type)
    normalized_quantity = validate_quantity(quantity)
    normalized_price = validate_price(normalized_type, price)

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "type": normalized_type,
        "quantity": normalized_quantity,
        "price": normalized_price,
    }

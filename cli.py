"""CLI entry point for the trading bot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from trading_bot.bot.logging_config import configure_logging  # type: ignore
    from trading_bot.bot.orders import OrderManager  # type: ignore
    from trading_bot.bot.validators import validate_order_inputs  # type: ignore
else:
    from .bot.logging_config import configure_logging
    from .bot.orders import OrderManager
    from .bot.validators import validate_order_inputs


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Binance Futures Testnet trading bot")
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, dest="order_type", help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, type=float, help="Positive order quantity")
    parser.add_argument("--price", type=float, help="Limit price, required for LIMIT orders")
    return parser


def print_order_request_summary(order: Dict[str, Any]) -> None:
    """Print a clean order summary before execution."""
    print("Order Request Summary")
    print("-" * 24)
    print(f"Symbol:      {order['symbol']}")
    print(f"Side:        {order['side']}")
    print(f"Type:        {order['type']}")
    print(f"Quantity:    {order['quantity']}")
    if order["type"] == "LIMIT":
        print(f"Price:       {order['price']}")
    print()


def print_order_response_details(response: Dict[str, Any]) -> None:
    """Print structured order response details."""
    print("Order Response Details")
    print("-" * 24)

    data = response.get("data") or {}
    error = response.get("error") or {}

    if response.get("success") and isinstance(data, dict):
        print(f"orderId:     {data.get('orderId', 'N/A')}")
        print(f"status:      {data.get('status', 'N/A')}")
        print(f"executedQty: {data.get('executedQty', 'N/A')}")
        print(f"avgPrice:    {data.get('avgPrice', 'N/A')}")
    else:
        print("orderId:     N/A")
        print("status:      N/A")
        print("executedQty: N/A")
        print("avgPrice:    N/A")
        print()
        print("Error Details")
        print("-" * 13)
        print(f"type:        {error.get('type', 'N/A')}")
        print(f"message:     {error.get('message', 'N/A')}")
        if error.get("code") is not None:
            print(f"code:        {error.get('code')}")
        if error.get("http_status") is not None:
            print(f"http_status: {error.get('http_status')}")

    print()
    banner = "SUCCESS" if response.get("success") else "FAILURE"
    print(f"Order {banner}")
    print("=" * (7 + len(banner)))


def main() -> int:
    """Run the CLI."""
    logger = configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        validated = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        logger.error("Validation failed: %s", exc)
        print("Order Request Summary")
        print("-" * 24)
        print("Validation failed before execution.")
        print()
        print("Order FAILURE")
        print("=============")
        print(f"Error: {exc}")
        return 1

    print_order_request_summary(validated)

    manager = OrderManager(logger=logger)
    response = manager.execute_order(
        symbol=str(validated["symbol"]),
        side=str(validated["side"]),
        order_type=str(validated["type"]),
        quantity=float(validated["quantity"]),
        price=validated["price"] if validated["price"] is None else float(validated["price"]),
    )

    print_order_response_details(response)
    return 0 if response.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())

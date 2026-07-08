"""Order placement service layer."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, Optional

from .client import (
    BinanceAPIError,
    BinanceConfigurationError,
    BinanceFuturesClient,
    BinanceNetworkError,
    OrderRequest,
)
from .logging_config import configure_logging


class OrderManager:
    """Execute validated orders via the Binance client."""

    def __init__(
        self,
        client: BinanceFuturesClient | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or configure_logging()
        self.client = client or BinanceFuturesClient(logger=self.logger)

    def execute_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Execute an order and normalize the result schema."""
        request = OrderRequest(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        try:
            data = self.client.place_order(request)
            return {"success": True, "data": data, "error": {}}
        except (BinanceConfigurationError, BinanceNetworkError, BinanceAPIError, ValueError) as exc:
            self.logger.exception("Order execution failed.")
            error = {
                "type": exc.__class__.__name__,
                "message": str(exc),
            }
            if isinstance(exc, BinanceAPIError):
                error["code"] = exc.code
                error["http_status"] = exc.http_status
            return {"success": False, "data": {}, "error": error}

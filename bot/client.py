"""Binance Futures Testnet client wrapper."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests import Session
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from .logging_config import configure_logging

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Base class for Binance client errors."""


class BinanceConfigurationError(BinanceClientError):
    """Raised when required credentials are missing."""


class BinanceNetworkError(BinanceClientError):
    """Raised when the network request fails."""


class BinanceAPIError(BinanceClientError):
    """Raised when Binance rejects a request."""

    def __init__(self, message: str, code: Any = None, http_status: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status


@dataclass(frozen=True)
class OrderRequest:
    """Normalized order request payload."""

    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None


class BinanceFuturesClient:
    """Thin REST client for Binance USDT-M Futures Testnet."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        session: Session | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or configure_logging()
        self.api_key = (api_key or os.getenv("BINANCE_API_KEY", "")).strip()
        self.api_secret = (api_secret or os.getenv("BINANCE_API_SECRET", "")).strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

        if not self.api_key or not self.api_secret:
            raise BinanceConfigurationError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in the environment."
            )

    def place_order(self, request: OrderRequest) -> Dict[str, Any]:
        """Place a signed order and return Binance's JSON response."""
        params = self._build_params(request)
        self.logger.debug("Order request payload: %s", params)

        try:
            response = self.session.post(
                f"{self.base_url}/fapi/v1/order",
                params=self._signed_params(params),
                timeout=self.timeout,
            )
            self.logger.debug(
                "HTTP response status=%s body=%s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()
        except (ConnectionError, Timeout) as exc:
            self.logger.exception("Network error while placing order.")
            raise BinanceNetworkError("Failed to reach Binance Futures Testnet.") from exc
        except HTTPError as exc:
            self.logger.exception("HTTP error while placing order.")
            raise self._raise_api_error_from_response(exc.response) from exc
        except RequestException as exc:
            self.logger.exception("Unexpected request failure while placing order.")
            raise BinanceNetworkError("Request failed while placing order.") from exc

        return self._parse_json(response)

    def _build_params(self, request: OrderRequest) -> Dict[str, Any]:
        """Build validated order parameters."""
        params: Dict[str, Any] = {
            "symbol": request.symbol,
            "side": request.side,
            "type": request.order_type,
            "quantity": self._format_number(request.quantity),
            "timestamp": int(time.time() * 1000),
        }

        if request.order_type == "LIMIT":
            params["price"] = self._format_number(request.price)
            params["timeInForce"] = "GTC"

        return params

    def _signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attach an HMAC SHA256 signature to the query parameters."""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed = dict(params)
        signed["signature"] = signature
        return signed

    def _raise_api_error_from_response(self, response: Optional[requests.Response]) -> BinanceAPIError:
        """Convert an HTTP error response into a typed API error."""
        if response is None:
            return BinanceAPIError("Binance returned an HTTP error with no response body.")

        try:
            payload = response.json()
        except ValueError:
            payload = {"msg": response.text}

        message = payload.get("msg") if isinstance(payload, dict) else str(payload)
        code = payload.get("code") if isinstance(payload, dict) else None
        self.logger.debug("API rejection payload: %s", payload)
        return BinanceAPIError(
            message or "Binance rejected the request.",
            code=code,
            http_status=response.status_code,
        )

    def _parse_json(self, response: requests.Response) -> Dict[str, Any]:
        """Parse the JSON response safely."""
        try:
            payload = response.json()
        except ValueError as exc:
            self.logger.exception("Non-JSON response returned by Binance.")
            raise BinanceNetworkError("Binance returned a non-JSON response.") from exc

        self.logger.debug("Parsed response payload: %s", payload)
        return payload

    @staticmethod
    def _format_number(value: float | None) -> str:
        """Format numbers for Binance query strings."""
        if value is None:
            raise ValueError("A numeric value is required.")
        formatted = format(float(value), "f").rstrip("0").rstrip(".")
        return formatted or "0"

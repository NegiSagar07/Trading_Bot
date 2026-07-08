# Trading Bot

A simplified Binance Futures Testnet (USDT-M) trading bot built with Python and `requests`.

## Setup on Linux

```bash
cd /home/negi/coding/assessment/trading-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

## Usage

Run the CLI directly from the project root. The bot automatically writes detailed logs to `trading_bot.log` inside this repository directory.

**Example 1: Market Order**

```bash
python3 cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Example 2: Limit Order**

```bash
python3 cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

## Assumptions

- **Environment:** Assumes a Unix-like environment (Linux/macOS) for setup commands.
- **Credentials:** Assumes the user has registered a funded Binance Futures Testnet account.
- **Dependencies:** Uses only the raw `requests` library to keep the codebase highly lightweight without heavy wrappers.
- **Network:** Assumes stable connectivity to [https://testnet.binancefuture.com](https://testnet.binancefuture.com).
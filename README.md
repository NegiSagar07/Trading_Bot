# Trading Bot

A simplified Binance Futures Testnet (USDT-M) trading bot built with Python and `requests`.

## Setup on Linux

```bash
cd /home/negi/coding/assessment/trading-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r trading_bot/requirements.txt
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

The bot writes detailed logs to `trading_bot.log` in the current working directory.

## Usage

Run the CLI directly from the project root:

```bash
python3 trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
python3 trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

For LIMIT orders, `--price` is required and `timeInForce=GTC` is automatically added.

## Notes

- The client uses the Binance Futures Testnet base URL: `https://testnet.binancefuture.com`
- Orders are signed with HMAC SHA256 using the `timestamp` query parameter.
- Only `requests` is required at runtime.
# Trading_Bot

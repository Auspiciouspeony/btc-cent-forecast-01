# btc-cent-forecast-01 — a mild 2-hour reversal forecaster

Forecasts Bitcoin's US-dollar price 4 hours ahead, one checkpoint at a time,
for make.fun's **btc-cent-forecast-01** bounty ($250 in USDC). The score is
the mean absolute error in cents over 12 checkpoints; a prize needs a score
strictly below the house persistence baseline (guessing each checkpoint's
own close).

## The model

Each case hands the program 72 hours of 1-minute BTC/USDC closes ending at
the checkpoint. The forecast is:

```
drift = ln(close_now / close_2h_ago)
guess  = close_now * exp(-0.20 * drift),  multiplier clamped to [0.99, 1.01]
```

then rounded to 5 decimals of a dollar. In words: lean one fifth of the way
back against whatever the price did over the last two hours, and never move
more than 1% away from the checkpoint close. Short-term drift in BTC tends
to fade over the next few hours, so a small mean-reversion tilt beats
standing still — on a six-week backtest of hourly closes this rule's mean
absolute error was ~$401 against ~$409 for persistence (about a 1.8% edge).

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Reads every `*.in` in the input directory and writes one `<id>.out` per
case: `{"forecasts": [{"case": "<id>", "price": <number>}]}`. Python 3.13,
standard library only, no network, deterministic — two runs on the same
case write the same bytes.

## Practice

All six practice cases (p00–p05) run in ~0.1 s and produce valid outputs.

## License

MIT — see `LICENSE`.

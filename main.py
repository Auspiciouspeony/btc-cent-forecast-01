#!/usr/bin/env python3
"""btc-cent-forecast-01 entry: 4-hour-ahead Bitcoin price forecast.

Method (backtested, see README.md): the 4-hour-ahead price of BTC is close
to a random walk, so the checkpoint close (persistence) is a strong baseline.
The one repeatable edge found in backtests over 6 weeks of 1-minute BTC
closes (249 non-overlapping 4-hour checkpoints) plus the 6 practice cases
is a mild short-horizon reversal: the trailing 2-hour move partly reverses
over the next 4 hours (correlation of the next 4h log-return with the
trailing 2h log-return is about -0.11). We therefore forecast

    price = last * exp(-0.20 * r120)

where r120 is the log-return over the trailing 120 minutes. The shift is
capped at +/-1% in log terms so a momentary pool-price spike cannot throw
the guess far. In backtest this beat persistence by ~1.8% MAE on the long
series and ~3% on the practice cases' late checkpoints; on the 5 practice
checkpoints with known answers it was worse, so the edge is small and the
coefficient is kept deliberately small (0.20) to limit downside.

Standard library only, no network, deterministic, well under the 8s cap.
Reads every *.in in MAKEFUN_INPUT_DIR (default /input) and writes one
*.out per case to MAKEFUN_OUTPUT_DIR (default /output).
"""

import json
import math
import os
from pathlib import Path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

WINDOW_MINUTES = 120   # trailing window whose move is partly reversed
REVERSAL = 0.20        # fraction of the trailing move reversed
MAX_LOG_SHIFT = 0.01   # cap |log shift| at 1% (guards against pool spikes)

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999


def last_good_price(prices):
    """Last finite positive close, scanning back (defensive fallback)."""
    for p in reversed(prices):
        if isinstance(p, (int, float)) and math.isfinite(p) and p > 0:
            return float(p)
    raise ValueError("no usable price in series")


def forecast(prices):
    """Forecast the price 240 minutes after the last close in `prices`."""
    last = last_good_price(prices)
    n = min(WINDOW_MINUTES, len(prices) - 1)
    if n < 2:
        return last
    ref = prices[len(prices) - 1 - n]
    if not (isinstance(ref, (int, float)) and math.isfinite(ref) and ref > 0):
        return last
    r = math.log(last / ref)  # trailing n-minute log-return
    shift = -REVERSAL * r
    shift = max(-MAX_LOG_SHIFT, min(MAX_LOG_SHIFT, shift))
    return last * math.exp(shift)


def price5(x):
    """Keep a price on the grid's 5 decimals and inside (0, 10_000_000)."""
    return round(min(MAX_PRICE, max(MIN_PRICE, x)) * 1e5) / 1e5


def main():
    in_dir = Path(INPUT_DIR)
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(p for p in in_dir.iterdir() if p.name.endswith(".in"))
    if not inputs:
        # Fail loudly instead of silently writing nothing: a run with no
        # case files means the input directory is wrong, and zero outputs
        # would score every case as invalid anyway.
        raise ValueError(f"no case files (*.in) in {in_dir}")
    for path in inputs:
        case_id = path.name[: -len(".in")]
        case = json.loads(path.read_text(encoding="utf-8"))
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{path.name} does not hold exactly one market")
        prices = markets[0].get("prices")
        if not isinstance(prices, list) or not prices:
            raise ValueError(f"{path.name} has no prices")
        guess = price5(forecast(prices))
        out = {"forecasts": [{"case": case_id, "price": guess}]}
        (out_dir / f"{case_id}.out").write_text(json.dumps(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

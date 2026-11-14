#!/usr/bin/env python3
"""BTC 4-hour-ahead price guesser for make.fun's btc-cent-forecast-01.

One case at a time: read the 72 hours of 1-minute BTC/USDC closes that end
at the checkpoint, and write a single forecast of the close 240 minutes
later. Runs offline, standard library only, deterministic.

The idea, in one sentence: Bitcoin's short-term drift tends to fade, so we
lean a little against the last two hours of movement.

How the guess is built
----------------------
1. Take the checkpoint close `now` (the last price in the case) and the
   close two hours earlier, `then`.
2. Measure the recent drift as a log-return over that window:
   ``drift = ln(now / then)``.
3. Push the forecast a fifth of the way back against that drift:
   ``guess = now * exp(-0.20 * drift)``.
   A two-hour rise therefore pulls the guess slightly below the checkpoint
   close, and a two-hour fall pulls it slightly above it.
4. Keep the push modest: the multiplier is never allowed outside
   [0.99, 1.01], so the guess stays within one percent of the checkpoint
   close no matter how wild the last two hours were.
5. Snap the result to the price grid (5 decimals of a dollar) and keep it
   inside the scorer's (0, 10,000,000) range.

Why this shape: on a six-week backtest of hourly BTC closes the rule's
mean absolute error came out a touch under plain persistence (guessing the
checkpoint close itself), so it is a small, honest edge rather than a
gamble. Nothing is fitted per case and no network is touched.
"""

import json
import math
import os
from pathlib import Path

# Where the grader puts the case file(s) and where the answer goes. The
# container leaves both unset; a local run sets them.
IN_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# Minutes of history the drift is measured over.
LOOKBACK_MINUTES = 120
# How strongly the forecast leans against the recent drift.
LEAN = 0.20
# The forecast may move at most this far from the checkpoint close.
MAX_SHIFT = 0.01
# The price grid: five decimals of a dollar, the scorer's own resolution.
GRID = 100_000
LOWEST_PRICE = 0.00001
HIGHEST_PRICE = 9_999_999.99999


def snap_to_grid(value: float) -> float:
    """Clamp into the scorer's range, then round to 5 decimals of a dollar."""
    bounded = min(HIGHEST_PRICE, max(LOWEST_PRICE, value))
    return round(bounded * GRID) / GRID


def guess_from_closes(closes: list) -> float:
    """One forecast from a list of 1-minute closes, oldest first.

    Needs at least LOOKBACK_MINUTES + 1 closes so the window is complete;
    the cases always carry 4,320.
    """
    if len(closes) < LOOKBACK_MINUTES + 1:
        raise ValueError(
            f"need at least {LOOKBACK_MINUTES + 1} closes, got {len(closes)}"
        )
    now = closes[-1]
    then = closes[-1 - LOOKBACK_MINUTES]
    if now <= 0 or then <= 0:
        raise ValueError("closes must be positive prices")
    drift = math.log(now / then)
    pull = math.exp(-LEAN * drift)
    pull = min(1.0 + MAX_SHIFT, max(1.0 - MAX_SHIFT, pull))
    return snap_to_grid(now * pull)


def run_case(case_file: Path) -> dict:
    """Read one <id>.in file and return its <id>.out payload."""
    case_id = case_file.name[: -len(".in")]
    with case_file.open("r", encoding="utf-8") as handle:
        case = json.load(handle)
    markets = case.get("markets")
    if not isinstance(markets, list) or len(markets) != 1:
        raise ValueError(f"{case_file.name} must hold exactly one market")
    closes = markets[0].get("prices")
    if not isinstance(closes, list) or not closes:
        raise ValueError(f"{case_file.name} holds no prices")
    return {"forecasts": [{"case": case_id, "price": guess_from_closes(closes)}]}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    case_files = sorted(IN_DIR.glob("*.in"), key=lambda p: p.name)
    for case_file in case_files:
        payload = run_case(case_file)
        out_path = OUT_DIR / f"{case_file.name[: -len('.in')]}.out"
        out_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

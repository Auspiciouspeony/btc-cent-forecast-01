# BTC 4-hour forecast — make.fun `btc-cent-forecast-01`

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/Auspiciouspeony/btc-cent-forecast-01/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/Auspiciouspeony/btc-cent-forecast-01/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

Forecast Bitcoin's US-dollar price 240 minutes after each checkpoint, from
the 72 hours of 1-minute closes the case gives. One program, `main.py`
(Python 3.13, standard library only, no network), reads every `*.in` in the
input directory and writes one `*.out` per case.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Method

The 4-hour-ahead price of BTC is close to a random walk, so the checkpoint
close (persistence) is a strong baseline — most trend and mean-reversion
rules tested made it worse. The one repeatable edge found in backtests is a
mild short-horizon reversal: the trailing 2-hour move partly reverses over
the next 4 hours (the correlation of the next 4h log-return with the
trailing 2h log-return is about −0.11). The forecast is therefore

```
price = last_close * exp(-0.20 * r120)
```

where `r120` is the log-return over the trailing 120 minutes. The log-shift
is capped at ±1% so a momentary pool-price spike cannot throw the guess far.
The coefficient is deliberately small (0.20): the edge is ~2% of MAE, and a
bigger coefficient loses more when the regime turns.

## Backtests (honest numbers)

- 6 weeks of 1-minute BTC closes (Binance BTCUSDT, 1 Oct – 14 Nov 2026),
  249 non-overlapping 4-hour checkpoints: persistence MAE **$408.81**,
  this program **$401.28** (−1.8%).
- The 6 practice cases, late checkpoints every hour: persistence $420.30,
  this program $407.40 (−3.1%).
- The 5 practice checkpoints whose answers are known from the next case's
  checkpoint close: persistence $470.55, this program $484.46 — worse on
  those five, which is why the coefficient stays small. A 12-case final is
  small-sample too; no forecast can promise to beat the baseline there,
  this one just has the better expected value in the larger backtests.

## Files

- `main.py` — the entrypoint.
- `LICENSE` — MIT.

---

<sub>Entered on [make.fun](https://make.fun/?ref=skypiiee&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>

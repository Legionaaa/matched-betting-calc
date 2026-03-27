# Matched Betting Calculator

A compact matched betting calculator written in Python with `NiceGUI`, designed as a narrow phone-style interface and able to run as a native desktop window on Windows.

If you're using this calculator for matched betting, you can find current UK free bet offers (e.g. Bet £10 Get £30) here:

[UK free bet offers](https://ukfreebetoffers.co.uk)

![Calculator Screenshot](images/darkmode.png)

## Features

- Bet types: `Qualifier`, `SNR`, and `Money Back`
- Inputs for `Stake`, `Back odds`, `Lay odds`, `Back commission`, and `Lay commission`
- `Cashback` input that appears only for `Money Back`
- Collapsed-by-default `Underlay / Overlay` advanced slider from `-50%` to `+50%`
- Rounded lay stake with a copy button
- Result view showing lay liability, bookmaker/exchange totals, and total profit
- Total profit uses the lower of the two rounded outcome totals
- Light/dark mode toggle with saved preference between launches
- Uses `images/logo.png` in the app and generates `images/logo.ico` for Windows builds
- Native Windows window via `pywebview`
- Single-file Windows packaging via `PyInstaller`

## Requirements

Install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

## Run locally

Linux/macOS:

```bash
python3 matched_betting_calc.py
```

Then open:

```text
http://127.0.0.1:8080
```

Windows:

```bat
python matched_betting_calc.py
```

or:

```bat
py matched_betting_calc.py
```

When run directly with Python on Windows, the app opens in a native desktop window. The taskbar/title-bar icon can still appear as the Python icon in development mode because the window is hosted by Python/pywebview.

## Build a standalone Windows EXE

Run either:

```bat
build_windows.bat
```

or:

```bat
package_windows.bat
```

Both build the same single-file executable at:

```text
dist\<timestamp>\MatchedBettingCalc.exe
```

For convenience, the most recent build is also copied to:

```text
dist\MatchedBettingCalc.exe
```

The latest built path is also written to:

```text
dist\latest_build.txt
```

The packaged `.exe` uses `images/logo.ico` as the Windows app icon.

## Example

Using a typical free bet offer:

- Stake: £10
- Back odds: 5.0
- Lay odds: 5.2
- Profit: ~£8.20

You can find similar UK offers here:

[UK free bet offers](https://ukfreebetoffers.co.uk)

## Formula notes

The calculator balances the lay stake using the bookmaker and exchange profit difference divided by:

```text
lay odds - lay commission
```

Formulas by mode:

```text
Qualifier:
lay stake = stake * (back odds - ((back odds - 1) * back commission))
            / (lay odds - lay commission)

Free Bet SNR:
lay stake = stake * ((back odds - 1) * (1 - back commission))
            / (lay odds - lay commission)

Money Back:
lay stake = (stake * (back odds - 1) * (1 - back commission) + stake - cashback)
            / (lay odds - lay commission)
```

Notes:

- Commissions are entered as percentages and applied to winnings
- The underlay/overlay slider adjusts the unrounded lay stake before rounding to 2 decimal places
- Total profit is shown as the lower of the two final rounded outcomes

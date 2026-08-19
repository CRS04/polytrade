# Poly-Maker

A market making bot for Polymarket prediction markets. This bot automates the process of providing liquidity to markets on Polymarket by maintaining orders on both sides of the book with configurable parameters. A summary of my experience running this bot is available [here](https://x.com/defiance_cr/status/1906774862254800934)

## Overview

Poly-Maker is a comprehensive solution for automated market making on Polymarket. It includes:

- Real-time order book monitoring via WebSockets
- Position management with risk controls
- Customizable trade parameters read from a local `config.json`
- Automated position merging functionality
- Sophisticated spread and price management

## Structure

The repository consists of several interconnected modules:

- `poly_data`: Core data management and market making logic
- `poly_merger`: Utility for merging positions (based on open-source Polymarket code)
- `poly_stats`: Account statistics tracking
- `poly_utils`: Shared utility functions
- `data_updater`: Separate module for collecting market information

## Requirements

- Python 3.9 with latest setuptools
- Node.js (for poly_merger)
- Polymarket account and API credentials
- Google Sheets API credentials (only for `data_updater` / `poly_stats`)

## Installation

1. **Clone the repository**:

The trading modules import each other as `poly_maker.*`, so the checkout directory
must be named `poly_maker`:

```
git clone https://github.com/CRS04/polytrade.git poly_maker
cd poly_maker
```

2. **Install Python dependencies**:
```
pip install -r requirements.txt
```

3. **Install Node.js dependencies for the merger**:
```
cd poly_merger
npm install
cd ..
```

4. **Set up environment variables**:
```
cp .env.example .env
```

5. **Configure your credentials in `.env`**:
- `PK`: Your private key for Polymarket
- `BROWSER_ADDRESS`: Your wallet address

Make sure your wallet has done at least one trade thru the UI so that the permissions are proper.

6. **Create your market configuration**:
```
cp config.example.json config.json
```
Fill in the real token IDs and sizing parameters. `config.json` is gitignored.

7. **Start the market making bot**:

Run it as a package from the *parent* directory of the checkout:
```
cd ..
python -m poly_maker.main
```

## Configuration

The bot reads its markets and hyperparameters from a JSON file, by default
`config.json` in the repository root. Set `CONFIG_JSON` in `.env` to point
somewhere else. See `config.example.json` for the schema:

- **markets**: one entry per market with `token1`/`token2`, `baseSize`,
  `minEdge` and `maxInventory`. Entries with `"active": false` are skipped.
- **hyperparameters**: global trading logic settings.

### Google Sheets modules (optional)

`update_markets.py` and `update_stats.py` still use the original Google Sheets
workflow and are independent of the trading bot. To use them, create a Google
Service Account, place its `credentials.json` in the main directory, copy the
[sample Google Sheet](https://docs.google.com/spreadsheets/d/1Kt6yGY7CZpB75cLJJAdWo7LSp9Oz7pjqfuVWwgtn7Ns/edit?gid=1884499063#gid=1884499063),
grant the service account edit permission and set `SPREADSHEET_URL` in `.env`.
These scripts use top-level imports, so run them from inside the repository
directory.


## Poly Merger

The `poly_merger` module is a particularly powerful utility that handles position merging on Polymarket. It's built on open-source Polymarket code and provides a smooth way to consolidate positions, reducing gas fees and improving capital efficiency.

## Important Notes

- This code interacts with real markets and can potentially lose real money
- Test thoroughly with small amounts before deploying with significant capital
- The `data_updater` is technically a separate repository but is included here for convenience

## License

MIT

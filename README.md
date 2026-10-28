# FundingLens

Read-only BTC/ETH funding evidence from Kraken and Deribit. Developer: gelenbedalen / KalenSolves.

## Run

Python 3.10+; no third-party dependencies.

```bash
python3 fundinglens.py BTC
python3 fundinglens.py ETH
python3 -m unittest -v test_fundinglens.py
```

## What it does

- Fetches actual public API data concurrently; no fixture fallback.
- Uses Kraken relativeFundingRate, not its absolute fundingRate.
- Preserves Deribit projected/accumulated funding_8h semantics.
- Returns source URLs, native symbols, source timestamps, freshness and raw records.
- Keeps inverse and linear contracts separate; no cross-venue yield ranking is asserted.
- Leaves unverified OI conversions null rather than guessing.

## Scope and evidence

Eight deterministic adapter tests cover rate semantics, missing data, source failure, suspended instruments, nonfinite numbers and testnet responses. Public API availability can vary by region. No trading, wallet custody, payment or investment recommendation is implemented.

This repository contains the standalone live-data adapters. A broader local prototype also includes MCP and UI demonstrations; that integration is not represented as a deployed public endpoint here.

## Grant status

On 28 October 2026 the Context Protocol live grant documentation said Batch 1 was closed and no Batch 2 date was available. No grant award or active funded application is claimed. No stake or payment was made.

## Official references

- https://docs.kraken.com/api-reference/market-data/get-tickers
- https://support.kraken.com/articles/4844359082772-linear-multi-collateral-derivatives-contract-specifications
- https://docs.deribit.com/api-reference/market-data/public-get_book_summary_by_instrument
- https://docs.ctxprotocol.com/grants

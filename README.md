# g15-bitcoin

## About

A Bitcoin ticker for g15 (using the Bitcoin Price Index by CoinBase currently). 

## Requirements

Requires g15composer and python.

## Setup

1. Run `nohup g15composer ~/g15Output &`
2. `git clone https://github.com/XertroV/g15-bitcoin.git`
3. Add the following cron job: `* * * * * cd ~/g15-bitcoin && python runTicker.py`
4. Wait

## Get Price History

If you want historical pricing please run getPriceHistory.py


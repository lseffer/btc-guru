# BTC guru

Hobby project for showing off some Machine Learning skills in addition to software engineering.

Predicting the price of `BTC/USD` price using historical OHLCV (open, high, low, close and volume) data.

I might return to this project to add more transparency about the error metrics and some backtesting.

**Update August 2019:**
Currently predicting the percentage movement in `BTC/USD` 24 hours ahead. This proved to have some problems as the model mostly predicts small movements centered around 0. A better approach might be to try and predict in what percentile the percent change will be based on all earlier historical price movements. That way the model might also guess very high or very low values.

## Setup

1. Sign up to [CoinApi](https://www.coinapi.io) and obtain an API token. 
2. Replace the dummy token in the `.env` file and replace the database credentials however you want. 
3. Run `make run` or `docker-compose up -d --build`

## Tests
To run unit tests and type checking build the images then run
`make tests`

## Architecture
* Using InfluxDB to store time series. 
* Serving the website with gunicorn
* Rate limit on the public api to prevent abuse
* Fetching hourly data from CoinApi and seeding the database with public cryptocurrency data in plain csv from a cryptocurrency data website. 
* Charts drawn with [Highstock](https://www.highcharts.com/blog/products/highstock/)
* Model is (currently) a Tensorflow one-layer recurrent neural network. 
  * Initial plan was to also utilize Tensorflow probability to get the confidence in the predictions to the front-end, but this first version does not include it.

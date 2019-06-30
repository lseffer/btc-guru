import pandas as pd

df = pd.read_csv('historical_data/bitstampUSD_1-min_data_2012-01-01_to_2019-03-13.csv')
df['ts'] = pd.to_datetime(df['Timestamp'], unit='s')
df = df.set_index('ts')
df_rs = df.resample('H').mean()
df_rs = df_rs.drop(columns=['Timestamp'])
df_rs = df_rs.drop(columns=['Volume (Currency)'])
df_rs = df_rs.drop(columns=['Volume_(Currency)'])
df_rs = df_rs.drop(columns=['Weighted_Price'])
df_rs.columns = ['open','high','low','close','volume']
df_rs = df_rs.interpolate()
df_rs = df_rs.reset_index()
df_rs.to_json('historical_btc_1h_2011-12-31_2019-03-13.json', orient='records')

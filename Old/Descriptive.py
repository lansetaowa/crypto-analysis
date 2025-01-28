# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 09:12:21 2024

@author: elisa
"""

import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# query btc price data
db_file = "prices/crypto.db"
conn = sqlite3.connect(db_file)
query = "SELECT * FROM btc_hourly order by time"
df = pd.read_sql(query, conn)

df.info()

df['utc_dt'] = pd.to_datetime(df['utc_dt'])
df['nyc_dt'] = df['utc_dt'].apply(lambda x: x.astimezone(ZoneInfo("America/New_York")))

df['year'] = df['utc_dt'].dt.year
df['month'] = df['utc_dt'].dt.month
df['day'] = df['utc_dt'].dt.day
df['weekday'] = df['utc_dt'].dt.weekday # Monday=0, Sunday=6
df['hour'] = df['utc_dt'].dt.hour

# outlier for timestamp 1595300400, remove this record
df = df[df['time']!=1595300400]

#-------------------- plot mean, min/max/25%/75%
#-----------by year/month/day
res = df.groupby(['year','month','day'])['avg'].describe().reset_index()
res['ymd'] = pd.to_datetime(res['year'].astype(str) + '-' + res['month'].astype(str) + '-' + res['day'].astype(str))

# only visualize for 2020 and later
res = res[res['year']>=2020]

plt.figure(figsize=(18,9))

# mean
plt.plot(res['ymd'],res['mean'],'r-',label='mean',linewidth=1)
# range
plt.fill_between(res['ymd'], res['min'], res['max'], color='grey', alpha=0.2, label='min-max range')
plt.fill_between(res['ymd'], res['25%'], res['75%'], color='blue', alpha=0.4, label='inter-quartile range')

plt.title('BTC Price Stats')
plt.xlabel('Year-Month-Day')
plt.ylabel('Price(USD)')
plt.legend()
plt.grid(linestyle='--', alpha=0.6)

#-----------by year/month
res = df.groupby(['year','month'])['avg'].describe().reset_index()
res['ym'] = pd.to_datetime(res['year'].astype(str) + '-' + res['month'].astype(str) + '-01')
res = res[res['year']>=2020]

plt.figure(figsize=(18,9))

# mean
plt.plot(res['ym'],res['mean'],'ro-',label='mean')
# range
plt.fill_between(res['ym'], res['min'], res['max'], color='grey', alpha=0.2, label='min-max range')
plt.fill_between(res['ym'], res['25%'], res['75%'], color='blue', alpha=0.4, label='inter-quartile range')

plt.title('BTC Price Stats')
plt.xlabel('Year-Month')
plt.ylabel('Price(USD)')
plt.legend()
plt.grid(linestyle='--', alpha=0.6)

#------------------- plot std
plt.figure(figsize=(18,9))

# std/mean
res['std_pct'] = res['std']*100/res['mean']

fig, ax1 = plt.subplots(figsize=(18,9))

ax1.plot(res['ym'],res['std'],'go-',label='BTC Std by Month')
ax1.set_xlabel('Year-Month')
ax1.set_ylabel('Standard Deviation (USD)')
ax1.legend(loc='upper left')

ax2 = ax1.twinx()
ax2.plot(res['ym'],res['std_pct'],'bs--',label='Std/Mean (%)',alpha=0.5)
ax2.set_ylabel('Std/Mean (%)')
ax2.legend(loc='upper right')

plt.title('BTC Standard Deviation and Std/Mean Percentage Over Time')
plt.grid(linestyle='--', alpha=0.6)

#-------------------hourly range distribution
df['minmax_range'] = df['high'] - df['low']
df['openclose_range'] = df['close'] - df['open']
df['ratio'] = np.abs(df['openclose_range']/df['minmax_range'])

range_df = df[df['year']>=2020]

res = range_df.groupby('year')['ratio'].describe()
res = range_df.groupby(['year','month'])['ratio'].describe()

res = range_df.groupby('year')['ratio'].quantile([x/10 for x in range(10)]).reset_index()
res = pd.pivot_table(res, values = 'ratio',index='year',columns='level_1')

res = range_df.groupby(['year','month'])['ratio'].quantile([x/10 for x in range(10)]).reset_index()
res = pd.pivot_table(res, values = 'ratio',index=['year','month'],columns='level_2')

res = range_df.groupby(['year','month'])['minmax_range'].describe()

#------plot ratio dist
fig, ax = plt.subplots(3,1,figsize=(12,15))

sns.histplot(x=range_df['ratio'],ax=ax[0],bins=50,color='blue',alpha=0.5)
ax[0].set_title('Ratio Distribution')

sns.kdeplot(x=range_df['ratio'],ax=ax[1],color='blue',fill=True,alpha=0.5)
ax[1].set_title('KDE of Ratio')

sns.boxplot(x=range_df['ratio'],ax=ax[2],color='blue')
ax[2].set_title('Boxplot of Ratio')
ax[2].grid(linestyle='--',alpha=0.5)

plt.tight_layout()

#-------plot ratio dist by year


#------------------hourly higher/lower ratio









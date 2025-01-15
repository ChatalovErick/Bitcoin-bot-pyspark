import asyncio
import time
from datetime import datetime
from tokenize import group
import numpy as np
import pandas as pd
import pymongo
import calendar
import math
import sys
import json
import requests
import ipaddress
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# ---------------- #
# MatchTrades data #
# ---------------- #

fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(8,6))

match_trades = pd.read_pickle("data gathering and storage/Data transfer and local storage/dailydata/MatchTrades_data/MatchTrades 04-11-2024.pickle")
#(match_trades["amount"].apply(float)).describe()

iqr =  (match_trades["price"].apply(float)).quantile(0.75) - (match_trades["price"].apply(float)).quantile(0.25)
h = 2*iqr*(len((match_trades["price"].apply(float)))**(-1/2))
bins = round((max((match_trades["price"].apply(float)))-min((match_trades["price"].apply(float))))/h)

#ax1.hist(match_trades["price"].apply(float),bins=39)  # Create a histogram with 30 bins

match_trades.set_index('trade_date', inplace=True)

# ---------------- #
# data from 21-22  #
date_22 = match_trades["21:22:14":"21:32:14"]
(date_22["price"].apply(float)).describe()

ax1.plot(list(range(0,len(date_22))),date_22["price"].apply(float))

# --------- #
# histogram #
iqr =  (date_22["price"].apply(float)).quantile(0.75) - (date_22["price"].apply(float)).quantile(0.25)
h = 2*iqr*(len((date_22["price"].apply(float)))**(-1/2))
bins = round((max((date_22["price"].apply(float)))-min((date_22["price"].apply(float))))/h)

ax2.hist(date_22["price"].apply(float),bins=bins)  # Create a histogram with 30 bins
#plt.show()

# ------------------- #
# pdf das matchtrades #
mean = (date_22["price"].apply(float)).mean()
std_dev = (date_22["price"].apply(float)).std()

x = np.linspace(mean - 4*std_dev, mean + 4*std_dev, 1000)

# Calculate the probability density function (PDF)
pdf = norm.pdf(x, mean, std_dev)

ax3.plot(x, pdf, 'k', linewidth=2)
plt.show()

# ------------------------------------------------------- #
# ------------------------------------------------------- #

# --------------- #
# data from 22-23 #
fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(8,6))

date_23 = match_trades["23:00:14":"24:00:00"]
ax1.plot(list(range(0,len(date_23))),date_23["price"].apply(float))

iqr =  (date_23["price"].apply(float)).quantile(0.75) - (date_23["price"].apply(float)).quantile(0.25)
h = 2*iqr*(len((date_23["price"].apply(float)))**(-1/2))
bins = round((max((date_23["price"].apply(float)))-min((date_23["price"].apply(float))))/h)

ax2.hist(date_23["price"].apply(float),bins=bins)  # Create a histogram with 30 bins

# ------------------- #
# pdf das matchtrades #
mean = (date_23["price"].apply(float)).mean()
std_dev = (date_23["price"].apply(float)).std()

x = np.linspace(mean - 4*std_dev, mean + 4*std_dev, 1000)

# Calculate the probability density function (PDF)
pdf = norm.pdf(x, mean, std_dev)

ax3.plot(x, pdf, 'k', linewidth=2)
plt.show()




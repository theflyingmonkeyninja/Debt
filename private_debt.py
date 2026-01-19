#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 18:04:31 2026

@author: dhananjay
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.dates as mdates


df_debt = pd.read_csv('z1-nonfin-debt.csv')

df_rec = pd.read_csv('recessionindicators.csv')


df_debt['Date'] = df_debt['date'].str.replace(
    ':', '-').apply(lambda x: pd.Period(x.replace(':', ''), freq='Q-MAR').start_time)

df_sectoral_debt = df_debt[['Date', 'Households and Nonprofits',
                            'Nonfinancial Business', 'State and Local Governments', 'GDP']]

df_sectoral_debt['Total Private Debt'] = df_sectoral_debt['Households and Nonprofits'] + \
    df_sectoral_debt['Nonfinancial Business']

df_sectoral_debt['Total Private Debt % GDP'] = df_sectoral_debt['Total Private Debt'] / \
    df_sectoral_debt['GDP']*100


df_sectoral_debt['Private Debt Velocity'] = df_sectoral_debt['Total Private Debt'] - \
    df_sectoral_debt['Total Private Debt'].shift(-4)

df_sectoral_debt['Private Debt Velocity'] = df_sectoral_debt['Private Debt Velocity'] / \
    df_sectoral_debt['Total Private Debt']

df_sectoral_debt['Private Debt Accleration'] = (
    df_sectoral_debt['Private Debt Velocity']-df_sectoral_debt['Private Debt Velocity'].shift(-4))

df1 = df_sectoral_debt.copy()

df1 = df1[df1['Date'] >= '1967-01-01']
 
df1['velocity_change'] =  df1['Private Debt Velocity'] - df1['Private Debt Velocity'].shift(-1)
df1['falling'] = df1['velocity_change']<0

velocity_falling = df1['Private Debt Velocity'].where(df1['falling'])
velocity_rising =  df1['Private Debt Velocity'].where(~df1['falling'])


fig, ax = plt.subplots(figsize=(10, 6),)

ax.plot(df1['Date'], df1['Private Debt Accleration'], color = 'black')
ax.fill_between(df_rec['observation_date'],
                ax.get_ylim()[0], ax.get_ylim()[1],
                where=df_rec['Recession'] == 1,
                color='gray', alpha=0.3, label='Recession')
ax.axhline(y=0, color='r', linestyle='-', alpha =0.6)


ax.set_title('US Private Debt Accleration vs. Recession Periods')
ax.set_ylabel('Debt velocity')
ax.legend()
plt.show()


#

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(df1['Date'], df1['Private Debt Velocity'], alpha=0.4, color='black')

ax.plot(df1['Date'], velocity_rising, color='green',linewidth=2)
ax.plot(df1['Date'], velocity_falling, color='red',linewidth=2)

ax.fill_between(df_rec['observation_date'],
                ax.get_ylim()[0], ax.get_ylim()[1],
                where=df_rec['Recession'] == 1,
                color='gray', alpha=0.2, label='Recession')


ax.set_title('US Private Debt Velocity vs. Recession Periods')
ax.set_ylabel('Debt accleration')
ax.legend()
plt.show()

Api_key="6ce523c65ffb8915dddf970acab037d6"

from fredapi import Fred
import pandas as pd

fred = Fred(api_key=Api_key)

series_codes = {
    # Delinquency
    "delinq_consumer": "DRCLACBS",
    "delinq_mortgage": "DRSFRMACBS",

    # Defaults / charge-offs
    "chargeoff_consumer": "CORCACBS",
    "chargeoff_creditcard": "CORCCACBS",

    # Recession
    "recession": "USRECQ"
}

start_date = "1980-01-01"

df = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_date)
    df[name] = s

df.index = pd.to_datetime(df.index)
df = df.sort_index()

print(df.tail())


max_lag = 8

print("HY correlations")
for k in range(0, max_lag):
    corr = df['Credit_Impulse'].corr(cds['HY_OAS'].shift(-k))
    print(f"Lag {k}: {corr:.2f}")

print("\nIG correlations")
for k in range(0, max_lag):
    corr = df['Credit_Impulse'].corr(cds['IG_OAS'].shift(-k))
    print(f"Lag {k}: {corr:.2f}")


fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(df.index, df['Credit_Impulse'], color='black', label='Credit Impulse')

ax.plot(
    cds.index,
    cds['HY_OAS'].shift(-2),
    color='red',
    linestyle='--',
    label='HY (shifted -2Q)'
)

ax.plot(
    cds.index,
    cds['IG_OAS'].shift(-4),
    color='blue',
    linestyle='--',
    label='IG (shifted -4Q)'
)

ax.legend()
plt.show()

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(df.index, df['Credit_Impulse'], color='black', label='Credit Impulse')
ax1.axhline(0, color='black', linewidth=0.8)

ax2 = ax1.twinx()
ax2.plot(cds.index, cds['HY_OAS'], color='red', alpha=0.7, label='HY spread')
ax2.plot(cds.index, cds['IG_OAS'], color='blue', alpha=0.7, label='IG spread')

ax1.set_title('Credit Impulse (Cause) vs Credit Spreads (Effect)')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()

fred = Fred(api_key="YOUR_FRED_API_KEY")

start_date = "1995-01-01"

hy = fred.get_series(
    "BAMLH0A0HYM2",
    observation_start=start_date
)

ig = fred.get_series(
    "BAMLC0A0CM",
    observation_start=start_date
)

df_spreads = pd.DataFrame({
    "HY_OAS": hy,
    "IG_OAS": ig
})

df_spreads.index = pd.to_datetime(df_spreads.index)
df_spreads = df_spreads.dropna()

df_spreads_q = (
    df_spreads
    .resample("Q")
    .mean()
)

df_spreads_q = df_spreads_q.sort_index(ascending=False)

df_all = df_credit.join(df_spreads_q, how="inner")


for k in range(0, 6):
    corr_hy = df_all["Credit_Impulse"].corr(
        df_all["HY_OAS"].shift(-k)
    )
    corr_ig = df_all["Credit_Impulse"].corr(
        df_all["IG_OAS"].shift(-k)
    )
    print(f"Lag {k}: HY={corr_hy:.2f}, IG={corr_ig:.2f}")


import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_all.index, df_all["Credit_Impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)

ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all["HY_OAS"], color="red", alpha=0.7, label="HY OAS")
ax2.plot(df_all.index, df_all["IG_OAS"], color="blue", alpha=0.7, label="IG OAS")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()


df_all[
    [
        "Credit_Impulse",
        "HY_OAS", "IG_OAS",
        "delinq_consumer",
        "chargeoff_consumer"
    ]
]


def zscore(series):
    return (series - series.mean()) / series.std()


df_all["HY_z"] = zscore(df_all["HY_OAS"])
df_all["IG_z"] = zscore(df_all["IG_OAS"])
df_all["Delinq_z"] = zscore(df_all["delinq_consumer"])
df_all["Default_z"] = zscore(df_all["chargeoff_consumer"])


df_all["HY_z_lag"] = df_all["HY_z"].shift(-1)
df_all["IG_z_lag"] = df_all["IG_z"].shift(-3)
df_all["Delinq_z_lag"] = df_all["Delinq_z"].shift(-3)
df_all["Default_z_lag"] = df_all["Default_z"].shift(-6)

df_all["Credit_Stress_Index"] = (
    df_all["HY_z_lag"] +
    df_all["IG_z_lag"] +
    df_all["Delinq_z_lag"] +
    df_all["Default_z_lag"]
) / 4

import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(
    df_all.index,
    df_all["Credit_Impulse"],
    color="black",
    label="Credit Impulse"
)
ax1.axhline(0, color="black", linewidth=0.8)

ax2 = ax1.twinx()
ax2.plot(
    df_all.index,
    df_all["Credit_Stress_Index"],
    color="red",
    linewidth=2,
    label="Credit Stress Index"
)

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.title("Credit Impulse (Cause) vs Integrated Credit Stress (Effect)")
plt.show()

import statsmodels.api as sm

X = pd.concat(
    [
        df_all["Credit_Impulse"].shift(0),
        df_all["Credit_Impulse"].shift(1),
        df_all["Credit_Impulse"].shift(2),
        df_all["Credit_Impulse"].shift(3),
    ],
    axis=1
)

X.columns = ["CI_0", "CI_1", "CI_2", "CI_3"]
X = sm.add_constant(X)

y = df_all["Credit_Stress_Index"]

model = sm.OLS(y, X, missing="drop").fit()
print(model.summary())


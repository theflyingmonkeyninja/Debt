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

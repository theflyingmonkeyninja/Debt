#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 18:21:29 2026

@author: dhananjay
"""


from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np

Api_key = "6ce523c65ffb8915dddf970acab037d6"
fred = Fred(api_key=Api_key)
# %% Non governmental non financial borrowings
 

series_codes = {

    # "private_debt":"QUSPAMUSDA",
    "private_debt": "QUSPAMUSDA",

    # GDP
    "gdp": "GDP",

    # Recession
    "recession": "USRECQ",
}

start_date = "1963-01-01"



df = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_date)
    df[name] = s

df.index = pd.to_datetime(df.index)
df = df.sort_index()


# %%##

df['private_debt'] = df['private_debt']

df['private_debt_velocity'] = df['private_debt']-df['private_debt'].shift(1)

df['private_debt_accleration'] = (df['private_debt_velocity']-df['private_debt_velocity'].shift(1))/df['gdp']
df['private_debt_accleration'] = df['private_debt_accleration'].rolling(window = 4, min_periods = 1).mean()   



df['private_debt_velocity'] = df['private_debt_velocity']/ df['gdp']   
df['private_debt_velocity'] = df['private_debt_velocity'].rolling(window = 4, min_periods = 1).mean()   

df.fillna(0, inplace=True)

df['Date'] = df.index.to_list()
df = df[df['Date'] >= '1965-01-01']


df['velocity_change'] = df['private_debt_velocity'] - df['private_debt_velocity'].shift(1)
df['falling'] = df['velocity_change'] < 0


velocity_falling = df['private_debt_velocity'].where(df['falling'])
velocity_rising = df['private_debt_velocity'].where(~df['falling'])

df['falling'] = df['private_debt_accleration'] < 0

accleration_negative = df['private_debt_accleration'].where(df['falling'])
accleration_positive = df['private_debt_accleration'].where(~df['falling'])


# %%## Credit flow and impulse plots



fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(df['Date'], df['private_debt_accleration'], alpha=0.5, color='black')
ax1.plot(df['Date'], accleration_negative, color='red', linewidth=2)
ax1.plot(df['Date'], accleration_positive, color='green', linewidth=2)
ax1.fill_between(df.index.to_list(),
                ax1.get_ylim()[0], ax1.get_ylim()[1],
                where=df['recession'] == 1,
                color='gray', alpha=0.3, label='Recession')
ax1.axhline(y=0, color='gray', linestyle='--')
ax1.set_title(' Credit impluse (private sector) ')
ax1.set_ylabel('Debt accleration')
ax1.legend()


ax2.plot(df['Date'], df['private_debt_velocity'], alpha=0.5, color='black')
ax2.plot(df['Date'], velocity_rising, color='green', linewidth=2)
ax2.plot(df['Date'], velocity_falling, color='red', linewidth=2)
ax2.fill_between(df.index.to_list(),
                ax2.get_ylim()[0], ax2.get_ylim()[1],
                where=df['recession'] == 1,
                color='gray', alpha=0.3, label='Recession')
ax2.axhline(y=0, color='gray', linestyle='--')
ax2.set_title('Flow of debt (Private sector)')
ax2.set_ylabel('Debt velocity')
ax2.legend()
plt.tight_layout()
plt.show()





# %% Other macro credit factors

series_codes = {
    
    # 10 year treasury
    "T10": "DGS10",

    # 2 year treasury
    "T2": "DGS2",

    # 10Y-2Y
    "10Y2Y": "T10Y2Y",

    # High yeild cds option
    "HY_OAS": "BAMLH0A0HYM2",

    # Investment grade cds option
    "IG_OAS": "BAMLC0A0CM",

    
    # Delinquency rate accross private sector
    "Business delinquency (%)": "DRBLACBS",    # business loan delinquency
    "Consumer delinquency (%)": "DRCLACBS",    # consumer loan delinquency
    "Mortgage delinquency (%)": "DRSFRMACBS",  # mortgage delinquency
    "Overall delinquency (%)": "DRALACBN",     # all loans

    # Defaults / charge-offs
    "chargeoff_consumer": "CORCACBS",
    "chargeoff_creditcard": "CORCCACBS"
    
    
}


start_date = "1985-01-01"

df_spreads = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_date)
    df_spreads[name] = s


df["Credit_Impulse"] = df['private_debt_accleration']

df_spreads_q = df_spreads.resample("QS").mean()

df_spreads['Date']=df_spreads.index.to_list()

df_all = df.join(df_spreads_q, how="inner")


for k in range(-10, 10):
    corr_hy = df_all["Credit_Impulse"].corr(df_all["HY_OAS"].shift(-k))
    corr_ig = df_all["Credit_Impulse"].corr(df_all["IG_OAS"].shift(-k))
    corr_10y2y = df_all["Credit_Impulse"].corr(df_all["10Y2Y"].shift(-k))
    
    
    print(f"Lag {k}: HY={corr_hy:.2f}, IG={corr_ig:.2f}, 10Y2Y={corr_10y2y:.2f}")


for k in range(-10, 10):
    
    corr_delc = df_all["Credit_Impulse"].corr(df_all["Consumer delinquency (%)"].shift(-k))
    corr_delb = df_all["Credit_Impulse"].corr(df_all["Business delinquency (%)"].shift(-k))
    corr_delm = df_all["Credit_Impulse"].corr(df_all["Mortgage delinquency (%)"].shift(-k))
    corr_def = df_all["Credit_Impulse"].corr(df_all["chargeoff_consumer"].shift(-k))
    
    print(f"Lag {k}: DelC={corr_delc:.2f}, DelB={corr_delb:.2f}, DelM={corr_delm:.2f}, DefC={corr_def:.2f}")



fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_all.index, df_all["Credit_Impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all["HY_OAS"], color="red", alpha=0.7, label="HY OAS")
ax2.plot(df_all.index, df_all["IG_OAS"], color="blue", alpha=0.7, label="IG OAS")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()




def zscore(series):
    return (series - series.mean()) / series.std()


df_all["HY_z"] = zscore(df_all["HY_OAS"])
df_all["IG_z"] = zscore(df_all["IG_OAS"])
df_all["Delinq_z"] = zscore(df_all["Consumer delinquency (%)"])
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





fig, (ax1, ax2) = plt.subplots(2)
ax1.plot(df_all['Date'], df_all['private_debt_accleration'], alpha=0.5, color='black')
ax1.fill_between(df.index.to_list(),
                ax1.get_ylim()[0], ax1.get_ylim()[1],
                where=df['recession'] == 1,
                color='gray', alpha=0.3, label='Recession')
ax1.axhline(y=0, color='gray', linestyle='--')
ax2.plot(df_all['Date'], df_all['10Y2Y'], alpha=0.5, color='black')
ax2.fill_between(df.index.to_list(),
                ax2.get_ylim()[0], ax2.get_ylim()[1],
                where=df['recession'] == 1,
                color='gray', alpha=0.3, label='Recession')
ax2.axhline(y=0, color='gray', linestyle='--')


plt.show()


# %%
# non financial series to proxy EBITA and PiK



series_codes = {


    # Corporate profits before tax as a proxy for EBITDA
    "corp_profit": "A464RC1Q027SBEA",

    # Corporate debt level
    "corp_debt": "NCBDBIQ027S",
    
    # corporate interest expense (net interest proxy for cash interest)
    "corp_interest_paid":"BOGZ1FA106130001Q",
    
    # corporate interest accrued (net interest proxy for cash interest)
    "corp_net_interest_paid":"BOGZ1FA106130003Q"
    
    
    
}

start_date = "1985-01-01"
df_corp = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_date)
    df_corp[name] = s


df_corp["corp_debt"] = df_corp["corp_debt"]*1e-3 
df_corp["corp_interest_paid"] = df_corp["corp_interest_paid"]*1e-3 
df_corp["corp_net_interest_paid"] = df_corp["corp_net_interest_paid"]*1e-3 

df_corp['EBIT_proxy'] = df_corp['corp_debt']/df_corp['corp_profit']
df_corp['Pik_proxy'] = df_corp['corp_net_interest_paid']/df_corp['corp_profit']


df_all = df_all.join(df_corp, how="inner")

df_all['Pik_delta'] = df_all['Pik_proxy'].diff(4)
df_all['Lev_delta'] = df_all['EBIT_proxy'].diff(4)


for k in range(-10, 10):
    corr_pik = df_all["Credit_Impulse"].corr(df_all["Pik_delta"].shift(-k))
    corr_ebit = df_all["Credit_Impulse"].corr(df_all["Lev_delta"].shift(-k))
    
    
    print(f"Lag {k}: PIK={corr_pik:.2f}, EBIT={corr_ebit:.2f}")


fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_all.index, df_all["Credit_Impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all["EBIT_proxy"], color="red", alpha=0.7, label="EBITDA proxy")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_all.index, df_all["Credit_Impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all["Pik_proxy"], color="blue", alpha=0.7, label="PiK proxy")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()



df_all['Implicit_Rate'] = (df_all['corp_net_interest_paid'] / df_all['corp_debt']) * 100

# 2. Cost-Adjusted PIK (Weighting the burden by current market spreads)
# This captures the "Refinancing Risk"
df_all['Cost_Adjusted_PIK'] = df_all['Pik_proxy'] * (1 + (df_all['HY_OAS'] / 100))

# 3. EBITDA Momentum (The speed of profit growth vs debt growth)
df_all['Profit_Growth'] = df_all['corp_profit'].pct_change(4)
df_all['Debt_Growth'] = df_all['corp_debt'].pct_change(4)
df_all['EBITDA_Gap'] = df_all['Debt_Growth'] - df_all['Profit_Growth']

# 4. Final 'Credit Stress' check
# Correlation between Impulse and the Gap between Debt and Profit growth
for k in range(-8, 9):
    c = df_all['Credit_Impulse'].corr(df_all['EBITDA_Gap'].shift(-k))
    print(f"Lag {k}: Impulse vs Leverage Gap = {c:.2f}")
    
fig, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(df_all.index, df_all['Credit_Impulse'], label='Credit Impulse', color='black')
ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all['EBITDA_Gap'], label='Debt-to-Profit Growth Gap', color='orange', alpha=0.7)
plt.title("Credit Acceleration vs. Leverage Expansion")
ax1.legend(loc=2); ax2.legend(loc=1)
plt.show()    


# --- 1. Refined PIK Stress (Interest Burden + Market Risk) ---
# We use the Z-score of the Cost-Adjusted PIK to make it unit-less
df_all['PIK_Stress'] = zscore(df_all['Pik_proxy'] * (1 + (df_all['HY_OAS'] / 100)))

# --- 2. Refined EBITDA Stress (The Leverage Gap) ---
# Positive value means Debt is growing faster than Profits
df_all['EBITDA_Stress'] = zscore(df_all['Debt_Growth'] - df_all['Profit_Growth'])

# --- 3. The Liquidity Stress (Credit Impulse Reversal) ---
# When Impulse falls, it's a withdrawal of liquidity. We invert it so "Stress" goes UP.
df_all['Impulse_Stress'] = zscore(-df_all['Credit_Impulse'])

# --- 4. Combine into the Financial Fragility Index (FFI) ---
# We apply a rolling mean to smooth out quarterly noise
df_all['Financial_Fragility_Index'] = (
    df_all['PIK_Stress'] + 
    df_all['EBITDA_Stress'] + 
    df_all['Impulse_Stress']
) / 3

df_all['FFI_Smoothed'] = df_all['Financial_Fragility_Index'].rolling(window=2).mean()


fig, ax1 = plt.subplots(figsize=(14,7))

# Plot Credit Impulse (The Driver)
ax1.plot(df_all.index, df_all['Credit_Impulse'], color='blue', alpha=0.4, label='Credit Impulse (Liquidity Flow)')
ax1.axhline(0, color='black', linewidth=1, linestyle='--')

# Plot Financial Fragility (The Resulting Stress)
ax2 = ax1.twinx()
ax2.plot(df_all.index, df_all['FFI_Smoothed'], color='crimson', linewidth=2, label='Financial Fragility Index (Stress)')

# Fill Recessions
ax1.fill_between(df_all.index, ax1.get_ylim()[0], ax1.get_ylim()[1], 
                 where=df_all['recession'] == 1, color='gray', alpha=0.2, label='Recession')

ax1.set_ylabel('Credit Impulse')
ax2.set_ylabel('Fragility Score (Z-Score)')
plt.title('The Credit Cycle: Liquidity Impulse vs. Balance Sheet Fragility')
ax1.legend(loc='upper left'); ax2.legend(loc='upper right')
plt.show()    
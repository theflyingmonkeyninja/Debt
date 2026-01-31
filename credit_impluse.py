from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np

Api_key = "6ce523c65ffb8915dddf970acab037d6"
fred = Fred(api_key=Api_key)

import matplotlib.pyplot as plt
import seaborn as sns

def apply_pro_style(font_scale=1.2):
    """
    Initializes the professional aesthetic defaults.
    """
    # Use Seaborn's base for scaling and white background
    sns.set_theme(style="white", font_scale=font_scale)
    
    # Global RcParams for deep customization
    plt.rcParams.update({
        'figure.dpi': 150,
        'figure.titlesize': 18,
        'axes.titlesize': 16,
        'axes.labelsize': 12,
        'legend.fontsize': 10,
        'legend.frameon': False,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'axes.grid': True,
        'grid.alpha': 0.2,
        'grid.linestyle': '--',
        'font.family': 'sans-serif',
        'font.sans-serif': ['Inter', 'Arial', 'DejaVu Sans'],
        'axes.prop_cycle': plt.cycler(color=["#4C72B0", "#55A868", "#C44E52", "#8172B3"])
    })

def finalize_plot(ax, title=None, xlabel=None, ylabel=None):
    """
    Fine-tunes a specific axis for a publication-ready look.
    Call this right before plt.show().
    """
    if title:
        # Left-aligning the title for a modern 'Economist' look
        ax.set_title(title, loc='left', fontweight='bold', pad=15)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
        
    sns.despine(ax=ax, trim=True)
    plt.tight_layout()

#%% Non governmental non financial borrowings
 

series_codes = {

    # "private_debt":"QUSPAMUSDA",
    "private_debt": "QUSPAMUSDA",

    # GDP
    "gdp": "GDP",

    # Recession
    "recession": "USRECQ",
    
    # Real GDP
    'real_gdp': "GDPC1"
}

start_observation_date = "1963-01-01"



df_macro = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_observation_date)
    df_macro[name] = s




#%%#

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

start_observation_date = "1985-01-01"
df_corp = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_observation_date)
    df_corp[name] = s

#%%#

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
    
    # Delinquency rate  business loan delinquency
    "Business delinquency (%)": "DRBLACBS",   

    # Delinquency rate  consumer loan delinquency 
    "Consumer delinquency (%)": "DRCLACBS",  
    
    # Delinquency rate  mortgage delinquency  
    "Mortgage delinquency (%)": "DRSFRMACBS",  

    # Delinquency rate  all  delinquency
    "Overall delinquency (%)": "DRALACBN",    

    # Defaults / charge-offs consumer
    "chargeoff_consumer": "CORCACBS",

    # Defaults / charge-offs credit card
    "chargeoff_creditcard": "CORCCACBS"
    
    
}


start_observation_date = "1985-01-01"

df_spreads = pd.DataFrame()

for name, code in series_codes.items():
    s = fred.get_series(code, observation_start=start_observation_date)
    df_spreads[name] = s

df_spreads=df_spreads.resample("QS").mean()

#%%# getting relavant macro variables

df_macro['observation_date'] = df_macro.index.to_list()

df_macro['deflator'] = df_macro['gdp']/df_macro['real_gdp']
df_macro['credit_flow'] = df_macro['private_debt'].diff()
df_macro['credit_impulse'] = df_macro['private_debt'].diff().diff()/df_macro['gdp']
df_macro['gdp_growth'] = df_macro['gdp'].diff()/df_macro['gdp']*100
df_macro['real_gdp_growth'] = df_macro['real_gdp'].diff()/df_macro['real_gdp']*100
df_macro['gdp_accleration'] = df_macro['gdp'].diff().diff()/df_macro['gdp']
df_macro['real_gdp_accleration'] = df_macro['real_gdp'].diff().diff()/df_macro['real_gdp']

#%%  smoothing macro variables by 4 quarters

df_macro['credit_flow'] = df_macro['credit_flow'].rolling(window=4).mean()
df_macro['credit_impulse'] = df_macro['credit_impulse'].rolling(window=4).mean()
df_macro['gdp_growth'] = df_macro['gdp_growth'].rolling(window=4).mean()
df_macro['real_gdp_growth'] = df_macro['real_gdp_growth'].rolling(window=4).mean()
df_macro['gdp_accleration'] = df_macro['gdp_accleration'].rolling(window=4).mean()
df_macro['real_gdp_accleration'] = df_macro['real_gdp_accleration'].rolling(window=4).mean() 


df_macro['velocity_change'] = df_macro['credit_flow'] - df_macro['credit_flow'].shift(1)
df_macro['falling'] = df_macro['velocity_change'] < 0


velocity_falling = df_macro['credit_flow'].where(df_macro['falling'])
velocity_rising = df_macro['credit_flow'].where(~df_macro['falling'])

df_macro['falling'] = df_macro['credit_impulse'] < 0

accleration_negative = df_macro['credit_impulse'].where(df_macro['falling'])
accleration_positive = df_macro['credit_impulse'].where(~df_macro['falling'])


# %%## Credit flow and impulse plots



fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(df_macro['observation_date'], df_macro['credit_impulse'], alpha=0.5, color='black')
ax1.plot(df_macro['observation_date'], accleration_negative, color='red', linewidth=2)
ax1.plot(df_macro['observation_date'], accleration_positive, color='green', linewidth=2)
ax1.fill_between(df_macro.index.to_list(),ax1.get_ylim()[0], ax1.get_ylim()[1], where=df_macro['recession'] == 1,color='gray', alpha=0.3, label='Recession')
ax1.axhline(y=0, color='gray', linestyle='--')
ax1.set_title(' Credit impulse (private sector) ')
ax1.set_ylabel('Debt accleration')
ax1.legend()


ax2.plot(df_macro['observation_date'], df_macro['credit_flow'], alpha=0.5, color='black')
ax2.plot(df_macro['observation_date'], velocity_rising, color='green', linewidth=2)
ax2.plot(df_macro['observation_date'], velocity_falling, color='red', linewidth=2)
ax2.fill_between(df_macro.index.to_list(), ax2.get_ylim()[0], ax2.get_ylim()[1], where=df_macro['recession'] == 1,color='gray', alpha=0.3, label='Recession')
ax2.axhline(y=0, color='gray', linestyle='--')
ax2.set_title('Flow of debt (Private sector)')
ax2.set_ylabel('Debt velocity')
ax2.legend()
plt.tight_layout()
plt.show()

lags = range(-12, 13)  # +/- 3 years (12 quarters)
correlations = []

df_clean = df_macro.dropna(subset=['credit_impulse', 'recession'])

for lag in lags:
    # A negative lag means 'Credit Impulse' at time (t-k) is correlated with Recession at time (t)
    corr = df_clean['recession'].corr(df_clean['credit_impulse'].shift(lag))
    correlations.append(corr)

# 4. Visualization
plt.figure(figsize=(12, 6))
plt.bar(lags, correlations, color='skyblue', edgecolor='navy', alpha=0.8)
plt.axhline(0, color='black', linewidth=0.8)
plt.xlabel('Lag in Quarters (Negative = Impulse Leads Recession)')
plt.ylabel('Correlation Coefficient')
plt.title('Lag Analysis: Credit Impulse vs. Recession Indicator')
plt.xticks(lags)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Find and annotate the peak correlation
max_corr_val = max(correlations, key=abs)
best_lag = lags[correlations.index(max_corr_val)]

plt.annotate(f'Peak Lead: {max_corr_val:.2f} at Lag {best_lag}', 
             xy=(best_lag, max_corr_val), 
             xytext=(best_lag + 1, max_corr_val + 0.05),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1))

plt.tight_layout()
plt.show()


#%%## Ponzi finance 

#1. Calculate the Gap
df_macro['impulse_gdp_gap'] = df_macro['credit_impulse'] - df_macro['real_gdp_accleration']

# 2. Lower the threshold slightly (from 0.5 to 0.25) 
# This ensures we don't miss the 2008 or 2000 buildups
threshold = df_macro['impulse_gdp_gap'].std() * 0.35

# 3. Refined Boolean
df_macro['bubble_signal'] = (df_macro['impulse_gdp_gap'] > threshold) & (df_macro['credit_impulse'] > 0)

# 4. Smoother Persistence: Use a rolling sum instead of a strict minimum
# This flags a period if the condition is met in at least 2 out of 3 quarters
df_macro['ponzi_refined'] = df_macro['bubble_signal'].rolling(window=4).sum() >= 2

df_macro['ponzi_refined'] = (df_macro['ponzi_refined']) & (df_macro['recession'].rolling(window=8).sum() == 0)


historical_events = [
    ("1969-04-01", "1969-12-01", "1969 Credit Crunch", "red", "Hit"),
    ("1977-01-01", "1980-03-01", "Great Inflation Overheating", "red", "Hit"),
    ("1993-01-01", "1994-06-01", "90s Recovery Artifact", "blue", "False Positive"),
    ("1998-01-01", "2000-03-01", "Dot-Com Bubble", "red", "Hit"),
    ("2004-01-01", "2007-01-01", "Great Housing Bubble", "red", "Hit"),
    ("2011-01-01", "2013-12-01", "QE/Refi Artifact", "blue", "False Positive"),
    ("2021-06-01", "2022-12-01", "Post-COVID Mania", "red", "Hit"),
]

# --- 2. Plotting Code ---
fig, ax1 = plt.subplots(figsize=(18, 9))

# Plot the main indicators
ax1.plot(df_macro['observation_date'], df_macro['credit_impulse'], 
         label='Credit Impulse', color='#1f77b4', lw=2.5, zorder=3)
ax1.plot(df_macro['observation_date'], df_macro['real_gdp_accleration'], 
         label='GDP Accel', color='#ff7f0e', ls='--', alpha=0.8, zorder=3)

# Shade the recession periods (Background)
ax1.fill_between(df_macro['observation_date'], -0.03, 0.03, 
                 where=df_macro['recession'] == 1, 
                 color='gray', alpha=0.15, label='Recession', zorder=1)

# Highlight the historical periods from the scorecard
for start, end, label, color, verdict in historical_events:
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    
    # Draw a shaded vertical span for the event
    ax1.axvspan(start_dt, end_dt, color=color, alpha=0.1, label='_nolegend_')
    
    # Add a text label at the top of the chart
    y_pos = 0.026 if verdict == "Hit" else 0.022
    ax1.text(start_dt + (end_dt - start_dt)/2, y_pos, label, 
             rotation=0, horizontalalignment='center', fontsize=9, 
             fontweight='bold', color=color, 
             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

# Final visual tweaks
ax1.axhline(0, color='black', lw=1.2, alpha=0.5)
ax1.set_ylim(-0.03, 0.03)
ax1.set_xlim(pd.to_datetime("1965-01-01"), df_macro['observation_date'].max())
ax1.set_title('Minsky Scorecard: Historical "Hits" (Red) vs "False Positives" (Blue)', fontsize=16)
ax1.set_ylabel('Acceleration Rate', fontsize=12)
ax1.legend(loc='lower left', frameon=True)

plt.tight_layout()
plt.show()

# %%

df_macro = df_macro.join(df_spreads, how='inner')

print('The correlation between spreads and lagged credit impluse are: ')

for k in range(-10, 10):
    corr_hy = df_macro["credit_impulse"].corr(df_macro["HY_OAS"].shift(-k))
    corr_ig = df_macro["credit_impulse"].corr(df_macro["IG_OAS"].shift(-k))
    corr_10y2y = df_macro["credit_impulse"].corr(df_macro["10Y2Y"].shift(-k))
    
    
    print(f"Lag {k}: HY={corr_hy:.2f}, IG={corr_ig:.2f}, 10Y2Y={corr_10y2y:.2f}")

print('The correlation between deliquency and lagged credit impluse are: ')

for k in range(-10, 10):
    
    corr_delc = df_macro["credit_impulse"].corr(df_macro["Consumer delinquency (%)"].shift(-k))
    corr_delb = df_macro["credit_impulse"].corr(df_macro["Business delinquency (%)"].shift(-k))
    corr_delm = df_macro["credit_impulse"].corr(df_macro["Mortgage delinquency (%)"].shift(-k))
    
    
    print(f"Lag {k}: DelC={corr_delc:.2f}, DelB={corr_delb:.2f}, DelM={corr_delm:.2f}")



fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_macro.index, df_macro["credit_impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_macro.index, df_macro["HY_OAS"], color="red", alpha=0.7, label="HY OAS")
ax2.plot(df_macro.index, df_macro["IG_OAS"], color="blue", alpha=0.7, label="IG OAS")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()

def zscore(series):
    return (series - series.mean()) / series.std()


df_macro["HY_z"] = zscore(df_macro["HY_OAS"])
df_macro["IG_z"] = zscore(df_macro["IG_OAS"])
df_macro["Delinq_z"] = zscore(df_macro["Consumer delinquency (%)"])
df_macro["Default_z"] = zscore(df_macro["chargeoff_consumer"])


df_macro["HY_z_lag"] = df_macro["HY_z"].shift(-1)
df_macro["IG_z_lag"] = df_macro["IG_z"].shift(-3)
df_macro["Delinq_z_lag"] = df_macro["Delinq_z"].shift(-3)
df_macro["Default_z_lag"] = df_macro["Default_z"].shift(-6)

df_macro["Credit_Stress_Index"] = (
    df_macro["HY_z_lag"] +
    df_macro["IG_z_lag"] +
    df_macro["Delinq_z_lag"] +
    df_macro["Default_z_lag"]
) / 4



X = pd.concat(
    [
        df_macro["credit_impulse"].shift(0),
        df_macro["credit_impulse"].shift(1),
        df_macro["credit_impulse"].shift(2),
        df_macro["credit_impulse"].shift(3),
    ],
    axis=1
)

X.columns = ["CI_0", "CI_1", "CI_2", "CI_3"]
X = sm.add_constant(X)

y = df_macro["Credit_Stress_Index"]

model = sm.OLS(y, X, missing="drop").fit()
print(model.summary())


fig, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(
    df_macro.index,
    df_macro["credit_impulse"],
    color="black",
    label="Credit Impulse"
)
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(
    df_macro.index,
    df_macro["Credit_Stress_Index"],
    color="red",
    linewidth=2,
    label="Credit Stress Index"
)
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.title("Credit Impulse (Cause) vs Integrated Credit Stress (Effect)")
plt.show()




df_corp["corp_debt"] = df_corp["corp_debt"]*1e-3 
df_corp["corp_interest_paid"] = df_corp["corp_interest_paid"]*1e-3 
df_corp["corp_net_interest_paid"] = df_corp["corp_net_interest_paid"]*1e-3 

df_corp['EBIT_proxy'] = df_corp['corp_debt']/df_corp['corp_profit']
df_corp['Pik_proxy'] = df_corp['corp_net_interest_paid']/df_corp['corp_profit']


df_macro = df_macro.join(df_corp, how="inner")

df_macro['Pik_delta'] = df_macro['Pik_proxy'].diff(4)
df_macro['Lev_delta'] = df_macro['EBIT_proxy'].diff(4)


for k in range(-10, 10):
    corr_pik = df_macro["credit_impulse"].corr(df_macro["Pik_delta"].shift(-k))
    corr_ebit = df_macro["credit_impulse"].corr(df_macro["Lev_delta"].shift(-k))
    
    
    print(f"Lag {k}: PIK={corr_pik:.2f}, EBIT={corr_ebit:.2f}")


fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_macro.index, df_macro["credit_impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_macro.index, df_macro["EBIT_proxy"], color="red", alpha=0.7, label="EBITDA proxy")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(df_macro.index, df_macro["credit_impulse"], color="black", label="Credit Impulse")
ax1.axhline(0, color="black", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(df_macro.index, df_macro["Pik_proxy"], color="blue", alpha=0.7, label="PiK proxy")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()



df_macro['Implicit_Rate'] = (df_macro['corp_net_interest_paid'] / df_macro['corp_debt']) * 100

# 2. Cost-Adjusted PIK (Weighting the burden by current market spreads)
# This captures the "Refinancing Risk"
df_macro['Cost_Adjusted_PIK'] = df_macro['Pik_proxy'] * (1 + (df_macro['HY_OAS'] / 100))

# 3. EBITDA Momentum (The speed of profit growth vs debt growth)
df_macro['Profit_Growth'] = df_macro['corp_profit'].pct_change(4)
df_macro['Debt_Growth'] = df_macro['corp_debt'].pct_change(4)
df_macro['EBITDA_Gap'] = df_macro['Debt_Growth'] - df_macro['Profit_Growth']

# 4. Final 'Credit Stress' check
# Correlation between Impulse and the Gap between Debt and Profit growth
for k in range(-8, 9):
    c = df_macro['credit_impulse'].corr(df_macro['EBITDA_Gap'].shift(-k))
    print(f"Lag {k}: Impulse vs Leverage Gap = {c:.2f}")
    
fig, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(df_macro.index, df_macro['credit_impulse'], label='Credit Impulse', color='black')
ax2 = ax1.twinx()
ax2.plot(df_macro.index, df_macro['EBITDA_Gap'], label='Debt-to-Profit Growth Gap', color='orange', alpha=0.7)
plt.title("Credit Acceleration vs. Leverage Expansion")
ax1.legend(loc=2); ax2.legend(loc=1)
plt.show()    


# --- 1. Refined PIK Stress (Interest Burden + Market Risk) ---
# We use the Z-score of the Cost-Adjusted PIK to make it unit-less
df_macro['PIK_Stress'] = zscore(df_macro['Pik_proxy'] * (1 + (df_macro['HY_OAS'] / 100)))

# --- 2. Refined EBITDA Stress (The Leverage Gap) ---
# Positive value means Debt is growing faster than Profits
df_macro['EBITDA_Stress'] = zscore(df_macro['Debt_Growth'] - df_macro['Profit_Growth'])

# --- 3. The Liquidity Stress (Credit Impulse Reversal) ---
# When Impulse falls, it's a withdrawal of liquidity. We invert it so "Stress" goes UP.
df_macro['Impulse_Stress'] = zscore(-df_macro['credit_impulse'])

# --- 4. Combine into the Financial Fragility Index (FFI) ---
# We apply a rolling mean to smooth out quarterly noise
df_macro['Financial_Fragility_Index'] = (
    df_macro['PIK_Stress'] + 
    df_macro['EBITDA_Stress'] + 
    df_macro['Impulse_Stress']
) / 3

df_macro['FFI_Smoothed'] = df_macro['Financial_Fragility_Index'].rolling(window=2).mean()


fig, ax1 = plt.subplots(figsize=(14,7))

# Plot Credit Impulse (The Driver)
ax1.plot(df_macro.index, df_macro['credit_impulse'], color='blue', alpha=0.4, label='Credit Impulse (Liquidity Flow)')
ax1.axhline(0, color='black', linewidth=1, linestyle='--')

# Plot Financial Fragility (The Resulting Stress)
ax2 = ax1.twinx()
ax2.plot(df_macro.index, df_macro['FFI_Smoothed'], color='crimson', linewidth=2, label='Financial Fragility Index (Stress)')

# Fill Recessions
ax1.fill_between(df_macro.index, ax1.get_ylim()[0], ax1.get_ylim()[1], 
                 where=df_macro['recession'] == 1, color='gray', alpha=0.2, label='Recession')

ax1.set_ylabel('Credit Impulse')
ax2.set_ylabel('Fragility Score (Z-Score)')
plt.title('The Credit Cycle: Liquidity Impulse vs. Balance Sheet Fragility')
ax1.legend(loc='upper left'); ax2.legend(loc='upper right')
plt.show()    
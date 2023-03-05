# %%
import pandas as pd

# %%
btc_usd = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/BTC-USD.csv')
#DAILY. Starts 2014-09-17
imf_energy = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/PNRGINDEXM.csv')
#MONTHLY. Starts 2014-09-01
ffer = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/FEDFUNDS.csv')
#MONTHLY. Starts 2014-09-01
m2 = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/M2SL.csv')
#MONTHLY. Starts 2014-09-01
michigan_exp = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/MICH.csv')
#MONTHLY Median expected price change next 12 months, Surveys of Consumers.

rate_real_post10 = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/REAINTRATREARAT10Y.csv')
#MONTHLY
mrkt_yield10 = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/DGS10.csv')
#DAILY
breakeven_inf10 = pd.read_csv(r'/Users/simitiangreg/Desktop/spring_23/data/T10YIE.csv')
#DAILY

# %%
import pandas as pd

def convert_to_float(column):
    return pd.to_numeric(column, errors='coerce').astype('float64')

mrkt_yield10['DGS10'] = convert_to_float(mrkt_yield10['DGS10'])
breakeven_inf10['T10YIE'] = convert_to_float(breakeven_inf10['T10YIE'])
rate_real_post10['REAINTRATREARAT10Y']= convert_to_float(rate_real_post10['REAINTRATREARAT10Y'])


# %%
def interpolate_and_impute(df, col, n):
    """
    This function takes a pandas dataframe with a date column and a value column, and interpolates
    the data into daily intervals using a polynomial of degree n. It then imputes the missing values
    using forward fill method.
    """
    # Make sure the date column is a datetime object
    df['DATE'] = pd.to_datetime(df['DATE'])

    # Set the date column as the index
    df = df.set_index('DATE')

    # Resample the dataframe to daily intervals
    df = df.resample('D').asfreq()

    # Interpolate the missing values using a polynomial of degree n
    df[col] = df[col].interpolate(method='polynomial', order=n)

    # Impute missing values using forward fill
    df[col] = df[col].fillna(method='ffill')

    # Reset the index and return the dataframe
    return df.reset_index()

mrkt_yield10 = interpolate_and_impute(mrkt_yield10,'DGS10', 3)
breakeven_inf10 = interpolate_and_impute(breakeven_inf10,'T10YIE', 3)
rate_real_post10_p3 = interpolate_and_impute(rate_real_post10,'REAINTRATREARAT10Y', 3)

# %%
#EXPERIMENT

rate_real_post10_p1 = interpolate_and_impute(rate_real_post10,'REAINTRATREARAT10Y', 1)
rate_real_post10_p5 = interpolate_and_impute(rate_real_post10,'REAINTRATREARAT10Y', 5)

merged_df = pd.merge(mrkt_yield10, breakeven_inf10, on='DATE', how='outer')
merged_df = pd.merge(merged_df, rate_real_post10_p3 , on='DATE', how='outer')
merged_df = merged_df.sort_values(by='DATE')

viz_copy_px = merged_df

viz_copy_px = merged_df.rename(columns={"REAINTRATREARAT10Y": "REAINTRATREARAT10Y_p3"})
viz_copy_px = pd.merge(viz_copy_px, rate_real_post10_p1 , on='DATE', how='outer')
viz_copy_px = viz_copy_px.rename(columns={"REAINTRATREARAT10Y": "REAINTRATREARAT10Y_p1"})
viz_copy_px = pd.merge(viz_copy_px, rate_real_post10_p5 , on='DATE', how='outer')
viz_copy_px = viz_copy_px.rename(columns={"REAINTRATREARAT10Y": "REAINTRATREARAT10Y_p5"})

viz_copy_px.head(5)

# %%
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle('Interpolation of Polynomial Degree 1 vs Degree 5')

x = viz_copy_px['DATE']

y1 = viz_copy_px['REAINTRATREARAT10Y_p1']
y2 = viz_copy_px['REAINTRATREARAT10Y_p5']

ax1.plot(x, y1)
ax2.plot(x, y2)


# %%
merged_df.columns

# %%
merged_df = merged_df.rename(columns={'DGS10':'mrkt_yield10', 'T10YIE': 'breakeven_inf10', "REAINTRATREARAT10Y": "rate_real_post10_p3"})
merged_df['rate_real_ante10'] = (((1+(merged_df['mrkt_yield10']/100))/((1+(merged_df['breakeven_inf10']/100))))-1)*100

# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, YearLocator


fig = plt.figure()
ax = plt.axes()

years = YearLocator()
date_formatter = DateFormatter('%Y')
plt.gca().xaxis.set_major_locator(years)
plt.gca().xaxis.set_major_formatter(date_formatter)

ax.plot(merged_df['DATE'], merged_df['rate_real_ante10'])
ax.plot(merged_df['DATE'], merged_df['rate_real_post10_p3'])
fig.suptitle('Ex-Post Real Rate vs. Ex-Ante Real Rate')




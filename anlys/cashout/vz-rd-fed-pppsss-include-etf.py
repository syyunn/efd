import pickle
with open("./anlys/cashout/rd-results-fed-pppsss-include-etf.pkl", "rb") as f:
    result = pickle.load(f)
    pass
pass

print(result['return(mean)'])

df = result[['first_name', 'last_name', 'ticker', 'return(mean)']]
print(len(df))

df['full_name'] = df['first_name'] + ' ' + df['last_name']
# Group by 'full_name' and 'ticker' and count the unique pairs
unique_pairs_count = df.groupby(['full_name', 'ticker']).size().reset_index(name='count').shape[0]
print("up", unique_pairs_count)

# Plot density using a kernel density estimation (KDE)
import numpy as np
import matplotlib.pyplot as plt

def remove_zeros(lst):
    return [x for x in lst if abs(x) > 0]

alphas = []
for row in result.itertuples():
    if row[3] != 0:
        alphas.append(row[8])


# Set labels for the left y-axis and x-axis
plt.xlabel('Excess return (%)')
plt.ylabel('Frequency')

# alphas = np.array(result_not_0['return(mean)'])
print(len(alphas)) 
# alphas = remove_zeros(alphas) # 0's because their was no matched ps chain.
# print(len(alphas)) 

print(np.mean(alphas))
print(np.std(alphas))
# compute length of elements of alpahs who are below 0 and above 0
print(len([x for x in alphas if x < 0]))
print(len([x for x in alphas if x == 0]))
print(len([x for x in alphas if x > 0]))
print(len([x for x in alphas if x > 5]))
print(len([x for x in alphas if x > 10]))
print(len([x for x in alphas if x > 20]))
print(len([x for x in alphas if x > 50]))
print(len([x for x in alphas if x > 100]))
print(len([x for x in alphas if x > 170]))



plt.hist(alphas, bins=100, density=False, alpha=0.7, color='b')

# Plot histogram (PDF) using a kernel density estimation (KDE)
n, bins = np.histogram(alphas, bins=100, density=True)

# Calculate CDF values based on the histogram data
cdf = np.cumsum(n) / np.sum(n)

# Create a second y-axis on the right side of the plot
ax2 = plt.gca().twinx()


# Plot the CDF on the right y-axis
ax2.plot(bins[:-1], cdf, color='r', label='CDF')

# Set labels for the right y-axis
ax2.set_ylabel('Cumulative Distribution (CDF)')
ax2.set_ylim([0, 1])  # Set the y-axis range for the CDF to [0, 1]

xtick_locs = np.arange(-100, 200, 10)  # Start at -100, end at 200 (exclusive), with a step of 10

# Define the corresponding x-tick labels as strings
xtick_labels = [str(x) for x in xtick_locs]

# Set the x-tick locations and labels
plt.xticks(xtick_locs, xtick_labels)


plt.title('Histogram/CDF of Excess Returns for U.S. Senators\' Stock Transactions')
plt.xlabel('Excess return (%)')

# Calculate the 50th percentile (CDF = 50%)
percentile_50 = np.percentile(alphas, 50)
# Add a vertical line at the 50th percentile
plt.axvline(percentile_50, color='r', linestyle='dashed', linewidth=1, label='CDF = 50%')

plt.axvline(x=np.mean(alphas), color='r', linestyle='--', label='mean=1.83')


plt.axvline(x=166.301137305, color='k', linestyle='--', label='Ron Wyden, Applied Materials Inc. (AMAT)')
plt.axvline(x=116.0954939177,color='b', linestyle='--', label='Ron Wyden, KLA Corporation (KLAC)')
plt.axvline(x=82.4176648637, color='lime', linestyle='--', label='Angus S King, Jr., Invesco QQQ ETF (Nasdaq-100 Index Fund)')

plt.axvline(x=70.9175031075, color='g', linestyle='--', label='Ron Wyden, Broadcom Inc. (AVGO)')

# Sector-speicfic ETFs
plt.axvline(x=56.8305065548, color='darkgrey', linestyle='--', label='John N. Kennedy, US Mid-Cap Momentum Fund (MTUM)')

plt.axvline(x=56.0920205291, color='tab:orange', linestyle='--', label='Sheldon Whitehouse, Communication Services Sector SPDR Fund (XLC)')
plt.axvline(x=44.3147151713, color='tab:blue', linestyle='--', label='Sheldon Whitehouse, US Medical Devices ETF (IHI)')
plt.axvline(x=43.8108676537, color='tab:red', linestyle='--', label='Mike Rounds, Vanguard Consumer Discretionary ETF (VCR)')

plt.axvline(x=40.2512815643, color='y', linestyle='--', label='David Perdue, Entegris Inc. (ENTG)')
plt.axvline(x=38.5832538245, color='m', linestyle='--', label='Ron Wyden, Constellation Brands, Inc. (STZ))')

plt.axvline(x=35.7462820713, color='salmon', linestyle='--', label='Timothy M Kaine, US Small-Cap Index Fund (VB)')


plt.axvline(x=30.8287735867, color='tab:purple', linestyle='--', label='Mike Rounds, Vanguard Financials Index Fund ETF (VFH)')

plt.axvline(x=20.5, color='tab:red', linestyle='--', label='Mark R Warner, Vanguard Vanguard Emerging Markets Index Fund ETF (VWO)')

plt.axvline(x=17.6038971585, color='tab:cyan', linestyle='--', label='Jerry Moran, Costco Wholesale Corporation (COST)')
plt.axvline(x=16.1457087974, color='midnightblue', linestyle='--', label='Shelley M. Capito, Clorox Company (CLX)')



# ETFs
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import skew, norm

# ... (existing code) ...

# Compute the skewness
alphas_array = np.array(alphas)
skewness = skew(alphas_array)
print(f"Skewness: {skewness}")

# Perform the hypothesis test for skewness
n = len(alphas_array)
standard_error_of_skewness = np.sqrt(6 * n * (n - 1) / ((n - 2) * (n + 1) * (n + 3)))
z_skewness = skewness / standard_error_of_skewness

# Set the significance level
alpha = 0.05
critical_value = norm.ppf(1 - alpha / 2)

# Check if we can reject the null hypothesis
if np.abs(z_skewness) > critical_value:
    print(f"The null hypothesis can be rejected at the {alpha} significance level. The distribution is not symmetric.")
else:
    print(f"The null hypothesis cannot be rejected at the {alpha} significance level. The distribution might be symmetric.")



plt.legend()
plt.ylabel('Density')
plt.show()


if __name__ == "__main__":
    pass
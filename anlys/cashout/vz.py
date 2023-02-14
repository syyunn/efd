import pickle
with open("./anlys/cashout/fifo-result.pickle", "rb") as f:
    result = pickle.load(f)

pass

# Plot density using a kernel density estimation (KDE)
import numpy as np
import matplotlib.pyplot as plt

alphas = np.array(result['return(amount_max)'])

def remove_zeros(lst):
    return [x for x in lst if abs(x) > 0]

alphas = remove_zeros(alphas) # 0's because their was no matched ps chain.

plt.hist(alphas, bins=100, density=True, alpha=0.7, color='b')
plt.title('Density Plot of Data')
plt.xlabel('Value')
plt.ylabel('Density')
plt.show()
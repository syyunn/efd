import pickle
with open("./anlys/cashout/result-rd.pkl", "rb") as f:
    result = pickle.load(f)
    pass
pass

print(result['return(mean)'])


# Plot density using a kernel density estimation (KDE)
import numpy as np
import matplotlib.pyplot as plt

def remove_zeros(lst):
    return [x for x in lst if abs(x) > 0]

alphas = np.array(result['return(mean)'])
# alphas = remove_zeros(alphas) # 0's because their was no matched ps chain.

plt.hist(alphas, bins=100, density=True, alpha=0.7, color='b')
plt.title('Density Plot of Data')
plt.xlabel('Value')
plt.ylabel('Density')
plt.show()

print(np.mean(alphas))
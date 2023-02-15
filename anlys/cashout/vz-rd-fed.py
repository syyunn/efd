import pickle
with open("./anlys/cashout/result-rd-fed.pkl", "rb") as f:
    result = pickle.load(f)
    pass
pass

print(result['return(mean)'])

df = result[['first_name', 'last_name', 'ticker', 'return(mean)']]

# Plot density using a kernel density estimation (KDE)
import numpy as np
import matplotlib.pyplot as plt

def remove_zeros(lst):
    return [x for x in lst if abs(x) > 0]

alphas = []
for row in result.itertuples():
    if row[4] != 0 and row[5] != 0:
        alphas.append(row[4])

# alphas = np.array(result_not_0['return(mean)'])
print(len(alphas)) 
# alphas = remove_zeros(alphas) # 0's because their was no matched ps chain.
# print(len(alphas)) 

print(np.mean(alphas))
print(np.std(alphas))
# compute length of elements of alpahs who are below 0 and above 0
print(len([x for x in alphas if x < 0]))
print(len([x for x in alphas if x > 0]))
print(len([x for x in alphas if x > 5]))
print(len([x for x in alphas if x > 10]))
print(len([x for x in alphas if x > 20]))
print(len([x for x in alphas if x > 50]))
print(len([x for x in alphas if x > 100]))
print(len([x for x in alphas if x > 170]))



plt.hist(alphas, bins=100, density=True, alpha=0.7, color='b')
plt.title('')
plt.xlabel('Excess return (%)')
plt.axvline(x=np.mean(alphas), color='r', linestyle='--', label='mean=3.04')
plt.axvline(x=170.6861090934, color='k', linestyle='--', label='Ron Wyden, AMAT')
plt.axvline(x=115.9061042942,color='b', linestyle='--', label='Ron Wyden, KLAC')
plt.axvline(x=70.895204555, color='g', linestyle='--', label='Ron Wyden, AVGO')
plt.axvline(x=10.2883291478, color='y', linestyle='--', label='David Perdue, BWXT')
plt.axvline(x=38.5832538245, color='m', linestyle='--', label='Ron Wyden, SZT')
# plt.axvline(x=np.mean(alphas), linestyle='--', label='mean=3.04')
plt.legend()
plt.ylabel('Density')
plt.show()





if __name__ == "__main__":
    pass
import pandas as pd
from tqdm import tqdm

import polygon
from polygon import RESTClient
from dotenv import load_dotenv
import os

import pickle
with open("./anlys/pppsss/nmavg_margins.pickle", "rb") as f:
    chanmavg_margins = pickle.load(f)
with open("./anlys/pppsss/nmavg_margins_spy.pickle", "rb") as f:
    chanmavg_margins_spy = pickle.load(f)

import matplotlib.pyplot as plt

# Define the data for the plot
x = chanmavg_margins_spy
y = [0 for _ in chanmavg_margins_spy]

# Create the plot
plt.scatter(x, y)

# Add labels to the axes
plt.xlabel('X axis')
plt.ylabel('Y axis')

# Show the plot
plt.savefig("./anlys/pppsss/normalized_avg_margins.png")
plt.show()
# plt.close()
pass

alphas = [margin-spy for margin, spy in zip(chanmavg_margins, chanmavg_margins_spy)]
bulls = [margin-spy for margin, spy in zip(chanmavg_margins, chanmavg_margins_spy) if margin > spy]
bears = [margin-spy for margin, spy in zip(chanmavg_margins, chanmavg_margins_spy) if margin < spy]
evens = [margin-spy for margin, spy in zip(chanmavg_margins, chanmavg_margins_spy) if margin == spy]

print(sum(bulls)/len(bulls))
print(sum(bears)/len(bears))
print(sum(evens)/len(evens))
print(sum(alphas)/len(alphas))

import matplotlib.pyplot as plt
import numpy as np

# List of floats

# Plot density using a kernel density estimation (KDE)
density = np.array(alphas)
plt.hist(density, bins=100, density=True, alpha=0.7, color='b')
plt.title('Density Plot of Data')
plt.xlabel('Value')
plt.ylabel('Density')
plt.show()
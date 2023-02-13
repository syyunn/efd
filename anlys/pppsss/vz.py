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

# import numpy as np

# # Define a sample list
# # Find the index of the top 5 largest elements
# top_5_indices = np.argsort(normalized_avg_margins)[-5:]

# # Print the index of the top 5 largest elements
# print("The index of the top 5 largest elements:", top_5_indices)
# print(np.array(normalized_avg_margins)[top_5_indices])
# print(np.array(chains)[top_5_indices[-5]])

# # draw with pppssss w/ graph
# # filter to compare with that periods' S&P 500

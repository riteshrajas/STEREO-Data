#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define the events and their paths
events = [
    {"target": "2010-08-31", "path": "STEREO_A_Events/Event_2010-08-31/STEREO_A_Event_2010-08-31.csv"},
    {"target": "2010-10-20", "path": "STEREO_A_Events/Event_2010-10-20/STEREO_A_Event_2010-10-20.csv"},
    {"target": "2010-11-02", "path": "STEREO_A_Events/Event_2010-11-02/STEREO_A_Event_2010-11-02.csv"},
    {"target": "2010-11-11", "path": "STEREO_B_Events/Event_2010-11-11/STEREO_B_Event_2010-11-11.csv"},
    {"target": "2011-01-21", "path": "STEREO_B_Events/Event_2011-01-21/STEREO_B_Event_2011-01-21.csv"}
]

dataframes = []

for event in events:
    if os.path.exists(event["path"]):
        df = pd.read_csv(event["path"])
        df['Time'] = pd.to_datetime(df['Time'])

        # Calculate relative time in days (t=0 is the start of the target date)
        target_time = pd.to_datetime(event["target"])
        df['Epoch_Days'] = (df['Time'] - target_time).dt.total_seconds() / (24 * 3600)

        df['Event'] = event["target"]
        dataframes.append(df)
    else:
        print(f"Missing data for {event['target']}")

# Combine all events into a single dataframe
all_data = pd.concat(dataframes, ignore_index=True)
print(f"Loaded {len(dataframes)} events, total rows: {len(all_data)}")

# Set up the figure with 3 subplots for the main variables
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
fig.suptitle('Superposed Epoch Analysis of STEREO Solar Energetic Particle Events', fontsize=16)

colors = plt.cm.tab10(np.linspace(0, 1, len(dataframes)))

# Plot Total Magnetic Field (BTotal)
for i, df in enumerate(dataframes):
    ax1.plot(df['Epoch_Days'], df['BTotal'], label=df['Event'].iloc[0], color=colors[i], alpha=0.7)
ax1.set_ylabel('Total Magnetic Field (nT)')
ax1.set_title('Magnetic Field Strength')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')

# Plot Solar Wind Speed (Vp)
for i, df in enumerate(dataframes):
    ax2.plot(df['Epoch_Days'], df['Vp'], label=df['Event'].iloc[0], color=colors[i], alpha=0.7)
ax2.set_ylabel('Solar Wind Speed (km/s)')
ax2.set_title('Proton Bulk Speed')
ax2.grid(True, alpha=0.3)

# Plot Proton Density (Np)
for i, df in enumerate(dataframes):
    ax3.plot(df['Epoch_Days'], df['Np'], label=df['Event'].iloc[0], color=colors[i], alpha=0.7)
ax3.set_ylabel('Proton Density (n/cc)')
ax3.set_title('Proton Number Density')
ax3.set_xlabel('Epoch Time (Days from Event Target Date)')
ax3.set_yscale('log') # Density often spans multiple orders of magnitude
ax3.grid(True, alpha=0.3)

# Add a vertical line at t=0 to mark the target date
for ax in [ax1, ax2, ax3]:
    ax.axvline(x=0, color='r', linestyle='--', alpha=0.5, label='Target Event')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()


# In[ ]:


import numpy as np
import matplotlib.pyplot as plt

# Calculate the median (or mean) across all events to find the true "superposed" signal
# First, we need to interpolate the data onto a common time grid since the exact 1-minute timestamps might not perfectly align relative to t=0

common_time_grid = np.linspace(-2, 3, 1000) # Grid from -2 days to +3 days
interpolated_data = { 'BTotal': [], 'Vp': [], 'Np': [] }

for df in dataframes:
    # We use numpy's interpolation to get the values at exactly our common time points
    b_interp = np.interp(common_time_grid, df['Epoch_Days'], df['BTotal'])
    v_interp = np.interp(common_time_grid, df['Epoch_Days'], df['Vp'])
    n_interp = np.interp(common_time_grid, df['Epoch_Days'], df['Np'])

    interpolated_data['BTotal'].append(b_interp)
    interpolated_data['Vp'].append(v_interp)
    interpolated_data['Np'].append(n_interp)

# Calculate the median across all events for each variable
median_BTotal = np.nanmedian(np.array(interpolated_data['BTotal']), axis=0)
median_Vp = np.nanmedian(np.array(interpolated_data['Vp']), axis=0)
median_Np = np.nanmedian(np.array(interpolated_data['Np']), axis=0)

# Plot the Superposed Epoch Analysis (Median Signal)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
fig.suptitle('Superposed Epoch Analysis - Median Event Signature', fontsize=16)

ax1.plot(common_time_grid, median_BTotal, color='blue', linewidth=2)
ax1.set_ylabel('Median B (nT)')
ax1.grid(True)
ax1.axvline(x=0, color='r', linestyle='--', alpha=0.5)

ax2.plot(common_time_grid, median_Vp, color='orange', linewidth=2)
ax2.set_ylabel('Median Vp (km/s)')
ax2.grid(True)
ax2.axvline(x=0, color='r', linestyle='--', alpha=0.5)

ax3.plot(common_time_grid, median_Np, color='green', linewidth=2)
ax3.set_ylabel('Median Np (n/cc)')
ax3.set_xlabel('Epoch Time (Days)')
ax3.set_yscale('log')
ax3.grid(True)
ax3.axvline(x=0, color='r', linestyle='--', alpha=0.5)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()


# ## Superposed Epoch Analysis
# 
# A Superposed Epoch Analysis (SEA) is a statistical technique used to reveal a weak signal or common pattern hidden in noisy data. By aligning multiple independent time series (like our 5 different solar events) to a common reference time (called the "epoch" or $t=0$), we can see how the variables generally behave before, during, and after an event. 
# 
# In the plots above, $t=0$ corresponds to the target date of each event. Negative values on the x-axis represent the days *before* the event, and positive values represent the days *after*. By overlaying all 5 events, we can visually inspect if there's a characteristic spike in solar wind speed, a drop in magnetic field, or any other repeating pattern that defines these SEP events.

# ## Superposed Epoch Analysis
# 
# A Superposed Epoch Analysis (SEA) is a statistical technique used to reveal a weak signal or common pattern hidden in noisy data. By aligning multiple independent time series (like our 5 different solar events) to a common reference time (called the "epoch" or $t=0$), we can see how the variables generally behave before, during, and after an event. 
# 
# In the plots above, $t=0$ corresponds to the target date of each event. Negative values on the x-axis represent the days *before* the event, and positive values represent the days *after*. By overlaying all 5 events, we can visually inspect if there's a characteristic spike in solar wind speed, a drop in magnetic field, or any other repeating pattern that defines these SEP events.

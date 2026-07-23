import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}

cells = []

# =========================================================================
# TITLE & INTRODUCTION
# =========================================================================
cells.append(new_markdown_cell("""# STEREO-A Event Data Visualization Suite

This notebook generates a comprehensive set of visualizations for the STEREO-A magnetic field and plasma data across 5 ICME event windows. Each visualization is saved as a PNG image in the `images/` directory, along with a description of what it shows.

## Events analyzed
| Target Date | Window Start | Window End |
|-------------|-------------|-----------|
| 2010-08-31  | 2010-08-29  | 2010-09-03 |
| 2010-10-20  | 2010-10-18  | 2010-10-23 |
| 2010-11-02  | 2010-10-31  | 2010-11-05 |
| 2010-11-11  | 2010-11-09  | 2010-11-14 |
| 2011-01-21  | 2011-01-19  | 2011-01-24 |

## Variables available
- **Magnetic Field**: BField_R, BField_T, BField_N, BTOTAL
- **Plasma**: Np (density), Vp (speed), Tp (temp), Vth (thermal speed)
- **Derived**: Beta, Entropy, Total_Pressure, Cone_Angle, Clock_Angle
- **Pressures**: Magnetic_Pressure, Dynamic_Pressure
- **Velocity cosines**: Vr, Vt, Vn ratios; Vp_RTN vector
- **Spacecraft position**: HAE, HEE, HEEQ, CARR, HCI coordinates, R (distance)
"""))

# =========================================================================
# IMPORTS & SETUP
# =========================================================================
cells.append(new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import seaborn as sns
from scipy import stats
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('dark_background')
sns.set_palette('bright')
figsize = (16, 8)
figsize_small = (10, 6)

# Create images directory
os.makedirs('images', exist_ok=True)

# Output directory
img_dir = 'images'

# Load all event CSVs
events = []
event_files = sorted([f for f in os.listdir('STEREO_A_Events') 
                      if f.startswith('Event_2010') or f.startswith('Event_2011')])
# Some dirs may have nested STEREO_B_Events — skip those
event_dirs = [d for d in os.listdir('STEREO_A_Events') 
              if d.startswith('Event_') and os.path.isdir(os.path.join('STEREO_A_Events', d))]

data = {}
for edir in sorted(event_dirs):
    target = edir.replace('Event_', '')
    csv_path = os.path.join('STEREO_A_Events', edir, f'STEREO_A_Event_{target}.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=['Time'])
        data[target] = df
        print(f'Loaded {target}: {len(df)} rows, {len(df.columns)-1} variables')

# Combine all data
all_data = pd.concat(data.values(), ignore_index=True)
print(f'\\nTotal rows: {len(all_data)}')
print(f'Columns: {list(all_data.columns)}')
"""))

cells.append(new_code_cell("""# Helper: save figure with description
def save_fig(fig, name, description=''):
    path = os.path.join(img_dir, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'Saved: {path}')
    if description:
        print(f'  -> {description}')
"""))

# =========================================================================
# GRAPH 1: Time series of all key variables — multi-panel
# =========================================================================
cells.append(new_markdown_cell("""## 1. Multi-Panel Time Series (Per Event: BField, Np, Vp, Tp, Beta)

Each event gets a 5-panel plot showing the core variables over the event window. This is the standard ICME overview plot used in solar physics."""))

cells.append(new_code_cell('''fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
labels = ['BField_R', 'BField_T', 'BField_N']
colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']

for target, df in data.items():
    t = df['Time']
    axes[0].plot(t, df['BTOTAL'], label=f'{target}', linewidth=0.8)
    
axes[0].set_ylabel('BTotal (nT)', fontsize=12)
axes[0].legend(fontsize=8, ncol=3)
axes[0].set_title('Total Magnetic Field |B| during all 5 Events', fontsize=14)

colors_events = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA']
for i, (target, df) in enumerate(data.items()):
    axes[1].plot(df['Time'], df['Np'], color=colors_events[i], label=target, linewidth=0.8)
axes[1].set_ylabel('Np (cm^-3)', fontsize=12)
axes[1].legend(fontsize=8)

for i, (target, df) in enumerate(data.items()):
    axes[2].plot(df['Time'], df['Vp'], color=colors_events[i], label=target, linewidth=0.8)
axes[2].set_ylabel('Vp (km/s)', fontsize=12)
axes[2].axhline(y=400, color='gray', linestyle='--', alpha=0.3, label='Slow wind threshold')

for i, (target, df) in enumerate(data.items()):
    axes[3].plot(df['Time'], df['Tp'], color=colors_events[i], label=target, linewidth=0.8)
axes[3].set_ylabel('Tp (K)', fontsize=12)

for i, (target, df) in enumerate(data.items()):
    axes[4].plot(df['Time'], df['Beta'], color=colors_events[i], label=target, linewidth=0.8)
axes[4].set_ylabel('Beta', fontsize=12)
axes[4].axhline(y=1, color='gray', linestyle='--', alpha=0.3)

axes[4].set_xlabel('Time', fontsize=12)
for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.grid(True, alpha=0.2)

plt.tight_layout()
fig.savefig(os.path.join(img_dir, '01_multipanel_timeseries.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/01_multipanel_timeseries.png')
print(' -> Shows BTOTAL, Np, Vp, Tp, and Beta for all 5 events overlaid. Note the Vp>400 threshold for fast solar wind and Beta<1 during magnetic clouds.')
'''))

# =========================================================================
# GRAPH 2: BTOTAL with BField RTN components — per event
# =========================================================================
cells.append(new_markdown_cell("""## 2. Magnetic Field Vector Components (RTN) per Event

Shows the decomposition of the magnetic field into Radial (R), Tangential (T), and Normal (N) components along with |B| for each event. The smooth rotation of the B-field vector is a signature of magnetic flux ropes (MCs)."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    
    axes[0].plot(df['Time'], df['BTOTAL'], color='white', linewidth=1.2)
    axes[0].set_ylabel('|B| (nT)', fontsize=11)
    axes[0].set_title(f'STEREO-A Magnetic Field Components - Event {target}', fontsize=14)
    
    axes[1].plot(df['Time'], df['BField_R'], color='#FF6B6B', linewidth=0.8)
    axes[1].set_ylabel('B_R (nT)', fontsize=11)
    axes[1].axhline(0, color='gray', linewidth=0.5)
    
    axes[2].plot(df['Time'], df['BField_T'], color='#4ECDC4', linewidth=0.8)
    axes[2].set_ylabel('B_T (nT)', fontsize=11)
    axes[2].axhline(0, color='gray', linewidth=0.5)
    
    axes[3].plot(df['Time'], df['BField_N'], color='#FFE66D', linewidth=0.8)
    axes[3].set_ylabel('B_N (nT)', fontsize=11)
    axes[3].axhline(0, color='gray', linewidth=0.5)
    axes[3].set_xlabel('Time', fontsize=11)
    
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'02_bfield_rtn_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: BTOTAL and B-field RTN components. Look for smooth rotation in B_T and B_N as flux rope signature.')
'''))

# =========================================================================
# GRAPH 3: Scatter — Np vs Vp
# =========================================================================
cells.append(new_markdown_cell("""## 3. Scatter Plots: Proton Density vs Speed

Standard dispersion plot. In normal solar wind, there is a well-known inverse correlation between Np and Vp (slow wind is denser). During ICMEs, this relationship breaks down."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, ax = plt.subplots(figsize=figsize_small)
    
    sc = ax.scatter(df['Np'], df['Vp'], c=df['Time'], cmap='viridis', s=5, alpha=0.6)
    plt.colorbar(sc, ax=ax, label='Time progression')
    ax.set_xlabel('Proton Density Np (cm^-3)', fontsize=12)
    ax.set_ylabel('Proton Speed Vp (km/s)', fontsize=12)
    ax.set_title(f'Np vs Vp Dispersion - Event {target}', fontsize=14)
    
    # Linear regression
    mask = df['Np'].notna() & df['Vp'].notna()
    if mask.sum() > 10:
        slope, intercept, r, p, se = stats.linregress(df.loc[mask, 'Np'], df.loc[mask, 'Vp'])
        x_fit = np.linspace(df['Np'].min(), df['Np'].max(), 100)
        ax.plot(x_fit, slope*x_fit + intercept, 'r--', alpha=0.5, label=f'r={r:.2f}')
        ax.legend()
    
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    fname = f'03_scatter_np_vp_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Np vs Vp with linear fit. Negative slope expected in quiet wind; deviations indicate ICME/shock disturbance.')
'''))

# =========================================================================
# GRAPH 4: Histograms / Distributions
# =========================================================================
cells.append(new_markdown_cell("""## 4. Histograms of Key Variables (All Events Overlaid)

Distribution plots reveal the statistical character of each event. ICME periods typically show elevated Tp, suppressed Beta, and possibly bimodal Vp (fast+slow wind)."""))

cells.append(new_code_cell('''variables_to_plot = ['BTOTAL', 'Np', 'Vp', 'Tp', 'Beta', 'Total_Pressure', 'Dynamic_Pressure', 'Entropy']
units = {'BTOTAL': 'nT', 'Np': 'cm^-3', 'Vp': 'km/s', 'Tp': 'K', 'Beta': '', 
         'Total_Pressure': 'nPa', 'Dynamic_Pressure': 'nPa', 'Entropy': ''}

fig, axes = plt.subplots(4, 2, figsize=(16, 20))
axes = axes.flatten()

for idx, var in enumerate(variables_to_plot):
    ax = axes[idx]
    for i, (target, df) in enumerate(data.items()):
        vals = df[var].dropna()
        if len(vals) > 0:
            ax.hist(vals, bins=60, alpha=0.4, label=target, color=colors_events[i], density=True)
    ax.set_xlabel(f'{var} ({units.get(var, "")})', fontsize=11)
    ax.set_ylabel('Probability Density', fontsize=11)
    ax.set_title(f'Distribution of {var}', fontsize=13)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.2)

plt.tight_layout()
fig.savefig(os.path.join(img_dir, '04_histograms_all.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/04_histograms_all.png')
print(' -> Probability density histograms for 8 key variables across all events overlaid. Shows whether distributions are unimodal/bimodal/skewed.')
'''))

# =========================================================================
# GRAPH 5: Correlation Heatmap
# =========================================================================
cells.append(new_markdown_cell("""## 5. Correlation Heatmap per Event

Pearson correlation matrix across all numerical variables — useful for identifying which parameters move together (e.g., Vp and Tp usually correlate; Beta and BTotal can be anti-correlated during MCs)."""))

cells.append(new_code_cell('''key_cols = ['BTOTAL', 'BField_R', 'BField_T', 'BField_N', 'Np', 'Vp', 'Tp', 'Vth',
            'Beta', 'Entropy', 'Total_Pressure', 'Magnetic_Pressure', 'Dynamic_Pressure', 'R']
titles_labels = {'BTOTAL': '|B|', 'BField_R': 'B_R', 'BField_T': 'B_T', 'BField_N': 'B_N',
                 'Np': 'Np', 'Vp': 'Vp', 'Tp': 'Tp', 'Vth': 'Vth',
                 'Beta': 'Beta', 'Entropy': 'Entropy', 'Total_Pressure': 'P_tot',
                 'Magnetic_Pressure': 'P_mag', 'Dynamic_Pressure': 'P_dyn', 'R': 'R(AU)'}

for target, df in data.items():
    df_key = df[key_cols].dropna()
    corr = df_key.corr()
    
    labels = [titles_labels[c] for c in key_cols]
    
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                xticklabels=labels, yticklabels=labels, ax=ax,
                vmin=-1, vmax=1, square=True, linewidths=0.5,
                annot_kws={'size': 7})
    ax.set_title(f'Correlation Matrix - {target}', fontsize=14, pad=20)
    plt.tight_layout()
    fname = f'05_corr_heatmap_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Pearson correlation matrix. Red=positive, Blue=negative. Strong Vp-Tp coupling and Beta-|B| anti-correlation are typical.')
'''))

# =========================================================================
# GRAPH 6: Box / Violin plots grouped by event
# =========================================================================
cells.append(new_markdown_cell("""## 6. Box Plots & Violin Plots by Event

These show the median, IQR, and outlier spread for each variable grouped per event — useful for comparing the typical state between events."""))

cells.append(new_code_cell('''box_vars = ['BTOTAL', 'Np', 'Vp', 'Tp', 'Beta', 'Total_Pressure', 'Dynamic_Pressure', 'Cone_Angle']

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for idx, var in enumerate(box_vars):
    ax = axes[idx]
    
    # Build a dataframe for seaborn
    plot_df = []
    for target, df in data.items():
        for val in df[var].dropna():
            plot_df.append({'Event': target, var: val})
    plot_df = pd.DataFrame(plot_df)
    
    sns.boxplot(data=plot_df, x='Event', y=var, ax=ax, palette='bright')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=8)
    ax.set_title(var, fontsize=12)
    ax.grid(True, alpha=0.2, axis='y')

plt.suptitle('Box Plots: Variable Distributions per Event', fontsize=16, y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(img_dir, '06_boxplots.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/06_boxplots.png')
print(' -> Box plots for 8 variables across all events. Compare medians, IQR, and outliers to see which event had extreme conditions.')
'''))

cells.append(new_code_cell('''# Violin plots (same variables but with distribution shape)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for idx, var in enumerate(box_vars):
    ax = axes[idx]
    plot_df = []
    for target, df in data.items():
        for val in df[var].dropna():
            plot_df.append({'Event': target, var: val})
    plot_df = pd.DataFrame(plot_df)
    
    sns.violinplot(data=plot_df, x='Event', y=var, ax=ax, palette='bright', inner='quartile')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=8)
    ax.set_title(var, fontsize=12)
    ax.grid(True, alpha=0.2, axis='y')

plt.suptitle('Violin Plots: Variable Distributions per Event', fontsize=16, y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(img_dir, '06b_violinplots.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/06b_violinplots.png')
print(' -> Violin plots show the full distribution shape (KDE) plus median/quartiles — reveals bimodality and tail behavior.')
'''))

# =========================================================================
# GRAPH 7: Sun-facing trajectory: X-Y in HEE coordinates
# =========================================================================
cells.append(new_markdown_cell("""## 7. Spacecraft Trajectory in HEE Coordinates (Heliocentric Earth Ecliptic)

The 2D trajectory in HEE X–Y shows how STEREO-A drifts ahead of Earth in its orbit over this date range. The Sun is at origin."""))

cells.append(new_code_cell('''fig, ax = plt.subplots(figsize=(10, 10))

for i, (target, df) in enumerate(data.items()):
    ax.plot(df['HEE_X'], df['HEE_Y'], label=target, color=colors_events[i], linewidth=1.5)
    # Mark start and end
    ax.scatter(df['HEE_X'].iloc[0], df['HEE_Y'].iloc[0], color=colors_events[i], s=80, marker='o', edgecolors='white', zorder=5)

# Sun
ax.scatter(0, 0, color='gold', s=300, marker='*', label='Sun', zorder=10)

# Orbit reference (1 AU circle)
theta = np.linspace(0, 2*np.pi, 200)
ax.plot(np.cos(theta), np.sin(theta), 'w--', alpha=0.2, label='1 AU reference')

ax.set_xlabel('HEE_X (AU)', fontsize=12)
ax.set_ylabel('HEE_Y (AU)', fontsize=12)
ax.set_title('STEREO-A Trajectory in HEE Coordinates', fontsize=14)
ax.set_aspect('equal')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.2)
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)

plt.tight_layout()
fig.savefig(os.path.join(img_dir, '07_hee_trajectory.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/07_hee_trajectory.png')
print(' -> Spacecraft position in HEE X-Y. Sun at origin. STEREO-A drifts ahead of Earth — note the increasing separation angle over time.')
'''))

# =========================================================================
# GRAPH 8: Helicocentric distance R over time
# =========================================================================
cells.append(new_markdown_cell("""## 8. Heliocentric Distance R over Time

Shows how far STEREO-A was from the Sun during each event window. Tiny variations (near 1 AU) but worth noting when interpreting plasma parameters."""))

cells.append(new_code_cell('''fig, ax = plt.subplots(figsize=figsize)
for i, (target, df) in enumerate(data.items()):
    ax.plot(df['Time'], df['R'], label=target, color=colors_events[i], linewidth=1.0)

ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Heliocentric Distance R (AU)', fontsize=12)
ax.set_title('STEREO-A Distance from Sun', fontsize=14)
ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.grid(True, alpha=0.2)

plt.tight_layout()
fig.savefig(os.path.join(img_dir, '08_distance_r.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/08_distance_r.png')
print(' -> Distance R(AU) over each event window. STEREO-A stays close to 1 AU; small orbital variations are visible at the end of each arc.')
'''))

# =========================================================================
# GRAPH 9: Pressure components stacked
# =========================================================================
cells.append(new_markdown_cell("""## 9. Pressure Components: Magnetic vs Dynamic vs Total

Shows the relative contribution of magnetic and ram (dynamic) pressures to the total pressure. During magnetic clouds, magnetic pressure can dominate."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, ax = plt.subplots(figsize=figsize)
    ax.fill_between(df['Time'], 0, df['Magnetic_Pressure'], alpha=0.5, label='Magnetic Pressure', color='#FF6B6B')
    ax.fill_between(df['Time'], df['Magnetic_Pressure'], df['Magnetic_Pressure']+df['Dynamic_Pressure'],
                    alpha=0.5, label='Dynamic Pressure', color='#4ECDC4')
    ax.plot(df['Time'], df['Total_Pressure'], color='white', linewidth=1.0, label='Total Pressure')
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Pressure (nPa)', fontsize=12)
    ax.set_title(f'Pressure Components - {target}', fontsize=14)
    ax.legend(fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'09_pressures_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Stacked area for magnetic & dynamic pressure, overlaid by total. When magnetic dominates, expect flux-rope/magnetic-cloud signature.')
'''))

# =========================================================================
# GRAPH 10: Cone Angle and Clock Angle time series
# =========================================================================
cells.append(new_markdown_cell("""## 10. Magnetic Field Orientation: Cone Angle & Clock Angle

**Cone angle** = angle of B w.r.t. radial direction (0 = anti-sunward, 180 = sunward). **Clock angle** = angle of B in the T-N plane. Smooth rotations in these angles indicate a magnetic flux rope."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    
    sc1 = axes[0].scatter(df['Time'], df['Cone_Angle'], c=df['BTOTAL'], cmap='plasma', s=3, alpha=0.7)
    axes[0].set_ylabel('Cone Angle (deg)', fontsize=11)
    axes[0].set_title(f'Magnetic Field Orientation - {target}', fontsize=14)
    plt.colorbar(sc1, ax=axes[0], label='|B| (nT)')
    axes[0].set_ylim(0, 180)
    
    sc2 = axes[1].scatter(df['Time'], df['Clock_Angle'], c=df['BTOTAL'], cmap='plasma', s=3, alpha=0.7)
    axes[1].set_ylabel('Clock Angle (deg)', fontsize=11)
    axes[1].set_xlabel('Time', fontsize=11)
    plt.colorbar(sc2, ax=axes[1], label='|B| (nT)')
    axes[1].set_ylim(-180, 180)
    
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'10_angles_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Cone (top) and Clock (bottom) angles, colored by |B|. Smooth large-scale rotations suggest flux-rope passage.')
'''))

# =========================================================================
# GRAPH 11: Pairwise KDE — Vp vs Tp
# =========================================================================
cells.append(new_markdown_cell("""## 11. 2D KDE / Joint Plots: Vp vs Tp

Kernel density estimation reveals where most of the data sits in (Vp, Tp) phase space, and the overall correlation."""))

cells.append(new_code_cell('''for target, df in data.items():
    sub = df[['Vp', 'Tp']].dropna()
    if len(sub) < 20:
        continue
    fig, ax = plt.subplots(figsize=(10, 8))
    
    try:
        sns.kdeplot(data=sub, x='Vp', y='Tp', fill=True, cmap='mako', bw_adjust=0.5, ax=ax)
    except Exception:
        pass
    ax.scatter(sub['Vp'], sub['Tp'], s=2, alpha=0.3, color='white')
    
    # Fit line
    slope, intercept, r, p, se = stats.linregress(sub['Vp'], sub['Tp'])
    x_fit = np.linspace(sub['Vp'].min(), sub['Vp'].max(), 100)
    ax.plot(x_fit, slope*x_fit + intercept, 'r--', label=f'fit: r={r:.2f}')
    
    ax.set_xlabel('Vp (km/s)', fontsize=12)
    ax.set_ylabel('Tp (K)', fontsize=12)
    ax.set_title(f'Joint KDE: Vp vs Tp - {target}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'11_kde_vp_tp_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: 2D KDE of Vp vs Tp. Tight positive correlation confirms wind speed-temperature relation; breakouts indicate ICME shock heating.')
'''))

# =========================================================================
# GRAPH 12: Velocity cosine polar plot (RTN direction)
# =========================================================================
cells.append(new_markdown_cell("""## 12. Velocity Direction Cosines (Polar / RTN)

Plots the proton flow direction cosines (Vr/V, Vt/V, Vn/V) at each timestamp. Near-unity Vr/V means radial (anti-sunward) flow; T and N components should be small."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    
    # Angle in TN-plane: atan2(Vt, Vn); radius = sqrt(Vt^2+Vn^2)
    theta = np.arctan2(df['Vt_Over_V_RTN'], df['Vn_Over_V_RTN'])
    r = np.sqrt(df['Vt_Over_V_RTN']**2 + df['Vn_Over_V_RTN']**2)
    
    sc = ax.scatter(theta, r, c=df['Vr_Over_V_RTN'], cmap='RdYlGn', s=3, alpha=0.5, vmin=0.9, vmax=1.05)
    plt.colorbar(sc, ax=ax, label='Vr/V (radial cos)')
    
    ax.set_title(f'Proton Flow Direction (TN-plane) - {target}', fontsize=14, pad=30)
    
    fname = f'12_velocity_polar_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Polar plot of transverse velocity components (Vt, Vn). Color=Vr/V. Radial flow expected (~Vr/V~1). Deviations suggest ICME deflection.')
'''))

# =========================================================================
# GRAPH 13: Beta vs |B| scatter colored by Tp
# =========================================================================
cells.append(new_markdown_cell("""## 13. Beta vs |B| Colored by Temperature

The plasma beta vs total magnetic field strength — when beta drops below 1 at high |B|, we are inside a magnetic cloud."""))

cells.append(new_code_cell('''for target, df in data.items():
    sub = df[['Beta', 'BTOTAL', 'Tp']].dropna()
    if len(sub) < 20:
        continue
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sc = ax.scatter(sub['BTOTAL'], sub['Beta'], c=sub['Tp'], cmap='inferno', s=5, alpha=0.7)
    plt.colorbar(sc, ax=ax, label='Tp (K)')
    ax.axhline(y=1, color='cyan', linestyle='--', alpha=0.5, label='Beta=1')
    ax.set_xlabel('|B| (nT)', fontsize=12)
    ax.set_ylabel('Beta', fontsize=12)
    ax.set_yscale('log')
    ax.set_title(f'Beta vs |B| (colored by Tp) - {target}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    fname = f'13_beta_vs_btotal_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Beta (log) vs |B| colored by Tp. Low-beta, high-|B|, hot regime = magnetic cloud interval.')
'''))

# =========================================================================
# GRAPH 14: Subplots of proton velocity cosines
# =========================================================================
cells.append(new_markdown_cell("""## 14. Velocity Direction Cosines time series

Shows Vr/V, Vt/V, Vn/V separately, exposing any transient non-radial flow (often seen at shock/sheath boundaries)."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, axes = plt.subplots(3, 1, figsize=(16, 9), sharex=True)
    
    axes[0].plot(df['Time'], df['Vr_Over_V_RTN'], color='#FF6B6B', linewidth=0.6)
    axes[0].set_ylabel('Vr / V', fontsize=11)
    axes[0].axhline(1, color='gray', linestyle='--', alpha=0.4)
    
    axes[1].plot(df['Time'], df['Vt_Over_V_RTN'], color='#4ECDC4', linewidth=0.6)
    axes[1].set_ylabel('Vt / V', fontsize=11)
    axes[1].axhline(0, color='gray', linestyle='--', alpha=0.4)
    
    axes[2].plot(df['Time'], df['Vn_Over_V_RTN'], color='#FFE66D', linewidth=0.6)
    axes[2].set_ylabel('Vn / V', fontsize=11)
    axes[2].axhline(0, color='gray', linestyle='--', alpha=0.4)
    axes[2].set_xlabel('Time', fontsize=11)
    
    axes[0].set_title(f'Velocity Direction Cosines (RTN) - {target}', fontsize=14)
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'14_velocity_cosines_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Vr/V should stay ~1. Excursions in Vt/V or Vn/V reveal non-radial flows at CME shocks/sheaths.')
'''))

# =========================================================================
# GRAPH 15: PairGrid / Pairplot per event (subset)
# =========================================================================
cells.append(new_markdown_cell("""## 15. Pair Plot (Subset of Key Variables)

Seaborn PairGrid showing pairwise scatter plots and marginal density for BTOTAL, Np, Vp, Tp, Beta."""))

cells.append(new_code_cell('''for target, df in data.items():
    cols = ['BTOTAL', 'Np', 'Vp', 'Tp', 'Beta']
    sub = df[cols].dropna()
    if len(sub) < 30:
        continue
    pair = sns.pairplot(sub, kind='scatter', diag_kind='kde', 
                         plot_kws={'s': 4, 'alpha': 0.3}, diag_kws={'common_norm': False})
    pair.fig.suptitle(f'Pair Plot - {target}', y=1.02, fontsize=14)
    fname = f'15_pairplot_{target}.png'
    pair.fig.savefig(os.path.join(img_dir, fname), dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(pair.fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Pairwise scatter + diagonal KDE for the 5 core variables. Diagonal shows marginal distribution; off-diagonal reveals joint structure.')
'''))

# =========================================================================
# GRAPH 16: Rolling/averaged Vp to find high-speed streams
# =========================================================================
cells.append(new_markdown_cell("""## 16. Rolling Mean of Vp (1-hour window)

Smoothed solar wind speed reveals high-speed streams (HSS) and slow wind intervals during each event."""))

cells.append(new_code_cell('''for target, df in data.items():
    df_sorted = df.sort_values('Time').copy()
    df_sorted['Vp_smooth'] = df_sorted['Vp'].rolling(window=60, min_periods=10).mean()  # 1 hour ~ 60 min
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df_sorted['Time'], df_sorted['Vp'], color='gray', alpha=0.4, label='Raw Vp')
    ax.plot(df_sorted['Time'], df_sorted['Vp_smooth'], color='#FF6B6B', linewidth=2, label='1h rolling avg')
    ax.axhspan(400, 800, color='gold', alpha=0.08, label='Fast wind region')
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Vp (km/s)', fontsize=12)
    ax.set_title(f'Smoothed Solar Wind Speed - {target}', fontsize=14)
    ax.legend(fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'16_vp_smoothed_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Raw vs 1h smoothed Vp. HSS revealed as intervals where smoothed Vp stays >400 km/s.')
'''))

# =========================================================================
# GRAPH 17: Entropy and Beta together (plasma state)
# =========================================================================
cells.append(new_markdown_cell("""## 17. Plasma Entropy and Beta Together

Proton entropy 超 S = ln(Tp^(3/2) / Np) combined with plasma beta 超 the two parameters often used to characterize solar wind mass/energy state."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    ax1.plot(df['Time'], df['Entropy'], color='#4ECDC4', linewidth=1.0, label='Entropy')
    ax1.set_ylabel('Entropy', fontsize=12, color='#4ECDC4')
    ax1.tick_params(axis='y', labelcolor='#4ECDC4')
    
    ax2.plot(df['Time'], df['Beta'], color='#FF6B6B', linewidth=1.0, label='Beta')
    ax2.set_ylabel('Beta', fontsize=12, color='#FF6B6B')
    ax2.tick_params(axis='y', labelcolor='#FF6B6B')
    ax2.axhline(y=1, color='white', linestyle='--', alpha=0.3)
    
    ax1.set_xlabel('Time', fontsize=12)
    ax1.set_title(f'Entropy & Beta - {target}', fontsize=14)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax1.grid(True, alpha=0.2)
    
    fname = f'17_entropy_beta_{target}.png'
    plt.tight_layout()
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Entropy (left axis) and Beta (right axis). Anti-correlation between them is typical: high entropy + low beta in dense, cool wind.')
'''))

# =========================================================================
# GRAPH 18: BField RTN in 3D (Time as 3rd axis)
# =========================================================================
cells.append(new_markdown_cell("""## 18. 3D Magnetic Field Vector Plot

A 3D scatter showing B_R, B_T, B_N at each timestamp, colored by |B|. This gives an intuitive picture of the field topology."""))

cells.append(new_code_cell('''from mpl_toolkits.mplot3d import Axes3D

for target, df in data.items():
    sub = df[['BField_R', 'BField_T', 'BField_N', 'BTOTAL']].dropna()
    if len(sub) < 20:
        continue
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    sc = ax.scatter(sub['BField_R'], sub['BField_T'], sub['BField_N'],
                    c=sub['BTOTAL'], cmap='plasma', s=3, alpha=0.5)
    plt.colorbar(sc, ax=ax, label='|B| (nT)', shrink=0.6)
    
    ax.set_xlabel('B_R (nT)')
    ax.set_ylabel('B_T (nT)')
    ax.set_zlabel('B_N (nT)')
    ax.set_title(f'3D Magnetic Field Vector - {target}', fontsize=14)
    
    fname = f'18_bfield_3d_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: 3D B-field components colored by |B|. Organized helical structure (instead of random cloud) indicates magnetic flux rope.')
'''))

# =========================================================================
# GRAPH 19: Autocorrelation of key variables
# =========================================================================
cells.append(new_markdown_cell("""## 19. Autocorrelation Functions

Shows how "memory" the time series has. Long autocorrelation tails imply coherent structures (e.g., magnetic clouds); short tails mean turbulent/random wind."""))

cells.append(new_code_cell('''from pandas.plotting import autocorrelation_plot

vars_acf = ['BTOTAL', 'Np', 'Vp', 'Tp', 'Beta']

for target, df in data.items():
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    for idx, var in enumerate(vars_acf):
        vals = df[var].dropna()
        if len(vals) > 50:
            autocorrelation_plot(vals.head(2000), ax=axes[idx])
            axes[idx].set_title(f'{var} ACF', fontsize=11)
    
    plt.suptitle(f'Autocorrelation Functions - {target}', fontsize=14, y=1.05)
    plt.tight_layout()
    fname = f'19_autocorrelation_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Autocorrelation for 5 key variables. Slow decay = coherent structure; rapid drop = turbulent, uncorrelated flow.')
'''))

# =========================================================================
# GRAPH 20: All-pressure comparison box plots
# =========================================================================
cells.append(new_markdown_cell("""## 20. Comparison of Pressure Types per Event

Side-by-side box plots for Magnetic, Dynamic, and Total Pressure across all events — to see how the pressure budget differs."""))

cells.append(new_code_cell('''pressure_cols = ['Magnetic_Pressure', 'Dynamic_Pressure', 'Total_Pressure']
titles_p = ['Magnetic Pressure', 'Dynamic Pressure', 'Total Pressure']

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for idx, (var, title_) in enumerate(zip(pressure_cols, titles_p)):
    plot_df = []
    for target, df in data.items():
        for val in df[var].dropna():
            plot_df.append({'Event': target, var: val})
    plot_df = pd.DataFrame(plot_df)
    
    sns.boxplot(data=plot_df, x='Event', y=var, ax=axes[idx], palette='bright')
    axes[idx].set_xticklabels(axes[idx].get_xticklabels(), rotation=45, fontsize=8)
    axes[idx].set_title(title_, fontsize=13)
    axes[idx].grid(True, alpha=0.2, axis='y')

plt.suptitle('Pressure Components per Event', fontsize=16, y=1.02)
plt.tight_layout()
fig.savefig(os.path.join(img_dir, '20_pressure_comparison.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/20_pressure_comparison.png')
print(' -> Box plots comparing magnetic/dynamic/total pressure across all events. Larger total-pressure outliers often coincide with CME impacts.')
'''))

# =========================================================================
# GRAPH 21: Hexbin joint plot (high density areas)
# =========================================================================
cells.append(new_markdown_cell("""## 21. Hexbin Density Plots (Np vs Vp)

Hexagonal binning is a more compact alternative to scatter plots when the dataset is huge — shows the density of points in phase space."""))

cells.append(new_code_cell('''for target, df in data.items():
    sub = df[['Np', 'Vp']].dropna()
    if len(sub) < 30:
        continue
    fig, ax = plt.subplots(figsize=(10, 8))
    
    hb = ax.hexbin(sub['Np'], sub['Vp'], gridsize=40, cmap='YlOrRd', mincnt=1)
    plt.colorbar(hb, ax=ax, label='Count in bin')
    
    ax.set_xlabel('Np (cm^-3)', fontsize=12)
    ax.set_ylabel('Vp (km/s)', fontsize=12)
    ax.set_title(f'Hexbin: Np vs Vp - {target}', fontsize=14)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    fname = f'21_hexbin_np_vp_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Hexbin density estimate of Np vs Vp. Bright hexes = common wind state; scattered outliers = CME driven.')
'''))

# =========================================================================
# GRAPH 22: Stacked histogram Vp by event (overlay)
# =========================================================================
cells.append(new_markdown_cell("""## 22. Step Histogram Overlay: Vp distribution per event

Step-style histograms on the same axis to directly compare wind speed populations between events."""))

cells.append(new_code_cell('''fig, ax = plt.subplots(figsize=figsize)
for i, (target, df) in enumerate(data.items()):
    vals = df['Vp'].dropna()
    ax.hist(vals, bins=80, histtype='step', linewidth=2, density=True, label=target, color=colors_events[i])

ax.set_xlabel('Vp (km/s)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('Vp Distribution Comparison Across Events', fontsize=14)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.2)

plt.tight_layout()
fig.savefig(os.path.join(img_dir, '22_vp_step_histogram.png'), dpi=150, bbox_inches='tight', facecolor='black')
plt.close(fig)
print('Saved: images/22_vp_step_histogram.png')
print(' -> Overlaid step histograms for Vp density per event. Bimodality indicates presence of both slow and fast wind streams in the window.')
'''))

# =========================================================================
# GRAPH 23: Lag-1 Scatter / Recurrence maps
# =========================================================================
cells.append(new_markdown_cell("""## 23. Lag Plots (1-minute Lag)

Plots each value vs its immediate predecessor. Strong positive correlations near the diagonal = coherent signal; scattered cloud = turbulent/noisy data."""))

cells.append(new_code_cell('''lag_vars = ['BTOTAL', 'Np', 'Vp', 'Tp', 'Beta']

for target, df in data.items():
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    for idx, var in enumerate(lag_vars):
        vals = df[var].dropna()
        if len(vals) > 30:
            axes[idx].scatter(vals[:-1], vals[1:], s=2, alpha=0.3, color=colors_events[idx])
            axes[idx].set_xlabel(f'{var}[t]')
            axes[idx].set_ylabel(f'{var}[t+1]')
            axes[idx].set_title(var, fontsize=11)
            axes[idx].grid(True, alpha=0.2)
    
    plt.suptitle(f'Lag-1 Plots - {target}', fontsize=14, y=1.05)
    plt.tight_layout()
    fname = f'23_lag_plots_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Lag-1 scatter. Points clustered along diagonal = memory in time; broad cloud = high-frequency turbulence.')
'''))

# =========================================================================
# GRAPH 24: Total Pressure vs Beta (with marker for cloud regime)
# =========================================================================
cells.append(new_markdown_cell("""## 24. Total Pressure vs Beta (MC Regime)

Low Beta + elevated Total Pressure typically indicates a *magnetic cloud* (a subset of ICMEs)."""))

cells.append(new_code_cell('''for target, df in data.items():
    sub = df[['Total_Pressure', 'Beta']].dropna()
    if len(sub) < 30:
        continue
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sc = ax.scatter(sub['Beta'], sub['Total_Pressure'], c=sub.index, cmap='viridis', s=5, alpha=0.5)
    plt.colorbar(sc, ax=ax, label='Time index')
    
    ax.axhline(sub['Total_Pressure'].median(), color='gray', linestyle='--', alpha=0.5, label='Median Ptot')
    ax.axvline(1, color='cyan', linestyle='--', alpha=0.5, label='Beta=1')
    
    ax.set_xlabel('Beta', fontsize=12)
    ax.set_ylabel('Total Pressure (nPa)', fontsize=12)
    ax.set_xscale('log')
    ax.set_title(f'Total Pressure vs Beta - {target}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    fname = f'24_ptot_vs_beta_{target}.png'
    plt.tight_layout()
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: Ptot vs Beta (log). Points with Beta<1 and elevated Ptot are inside magnetic cloud (MC) regime.')
'''))

# =========================================================================
# GRAPH 25: Summary — 6-panel dashboard per event
# =========================================================================
cells.append(new_markdown_cell("""## 25. Six-Panel Dashboard per Event (Final Summary Plot)

A consolidated dashboard combining the most informative views per event for a quick diagnostic."""))

cells.append(new_code_cell('''for target, df in data.items():
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    t = df['Time']
    
    # Row 1: BTOTAL, Np, Vp
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t, df['BTOTAL'], color='white', linewidth=0.8, label='|B|')
    ax1.set_ylabel('|B| (nT)'); ax1.legend(fontsize=8); ax1.grid(True, alpha=0.2)
    
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t, df['Np'], color='#4ECDC4', linewidth=0.8)
    ax2.set_ylabel('Np (cm^-3)'); ax2.grid(True, alpha=0.2)
    
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(t, df['Vp'], color='#FF6B6B', linewidth=0.8)
    ax3.set_ylabel('Vp (km/s)'); ax3.grid(True, alpha=0.2)
    
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.plot(t, df['Tp'], color='#FFE66D', linewidth=0.8)
    ax4.set_ylabel('Tp (K)'); ax4.grid(True, alpha=0.2)
    
    # Row 2: Beta, Total Pressure, Clock Angle
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.plot(t, df['Beta'], color='#AA96DA', linewidth=0.8)
    ax5.set_ylabel('Beta'); ax5.axhline(1, color='gray', linestyle='--', alpha=0.3)
    ax5.grid(True, alpha=0.2)
    
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.plot(t, df['Total_Pressure'], color='#F38181', linewidth=0.8)
    ax6.set_ylabel('P_tot (nPa)'); ax6.grid(True, alpha=0.2)
    
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.scatter(df['Cone_Angle'], df['Clock_Angle'], c=df['BTOTAL'], cmap='plasma', s=3, alpha=0.5)
    ax7.set_xlabel('Cone Angle (deg)'); ax7.set_ylabel('Clock Angle (deg)')
    
    fig.suptitle(f'Dashboard: {target}', fontsize=18, y=0.95)
    
    for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    
    fname = f'25_dashboard_{target}.png'
    fig.savefig(os.path.join(img_dir, fname), dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f'Saved: images/{fname}')
    print(f'  -> Event {target}: 6-panel dashboard combining timeseries + angle scatter for at-a-glance diagnosis.')
'''))

# =========================================================================
# FINAL SUMMARY
# =========================================================================
cells.append(new_markdown_cell("""## Summary of All Generated Images

The cell below lists every image file saved in `images/` with its filename.

| # | Filename | Type | Description |
|---|----------|------|-------------|
| 01 | `01_multipanel_timeseries.png` | Multi-panel time series | BTOTAL, Np, Vp, Tp, Beta overlaid for all events |
| 02 | `02_bfield_rtn_<date>.png` | Time series × 5 files | B-field RTN components per event (rotation = flux rope) |
| 03 | `03_scatter_np_vp_<date>.png` | Scatter + regression | Np vs Vp with linear fit per event |
| 04 | `04_histograms_all.png` | Histograms | Density histograms for 8 variables across events |
| 05 | `05_corr_heatmap_<date>.png` | Heatmap | Pearson correlation matrices per event |
| 06 | `06_boxplots.png` | Box plots | Distribution comparison per event (8 variables) |
| 06b | `06b_violinplots.png` | Violin plots | Distribution shape per event (8 variables) |
| 07 | `07_hee_trajectory.png` | 2D trajectory | Spacecraft path in HEE X-Y plane |
| 08 | `08_distance_r.png` | Time series | Heliocentric distance R over time |
| 09 | `09_pressures_<date>.png` | Stacked area | Magnetic + Dynamic + Total pressure per event |
| 10 | `10_angles_<date>.png` | Colored scatter | Cone & Clock angles colored by |B| |
| 11 | `11_kde_vp_tp_<date>.png` | 2D KDE | Vp vs Tp joint density per event |
| 12 | `12_velocity_polar_<date>.png` | Polar plot | Velocity direction cosines per event |
| 13 | `13_beta_vs_btotal_<date>.png` | Log-log scatter | Beta vs |B| colored by Tp |
| 14 | `14_velocity_cosines_<date>.png` | Time series | Vr/V, Vt/V, Vn/V per event |
| 15 | `15_pairplot_<date>.png` | Pair plot | Pairwise scatter + KDE for 5 core variables |
| 16 | `16_vp_smoothed_<date>.png` | Rolling mean | Raw vs 1h-smoothed Vp |
| 17 | `17_entropy_beta_<date>.png` | Dual-axis time series | Entropy & Beta together |
| 18 | `18_bfield_3d_<date>.png` | 3D scatter | 3D B_R/B_T/B_N colored by |B| |
| 19 | `19_autocorrelation_<date>.png` | ACF plot | Autocorrelation for 5 variables per event |
| 20 | `20_pressure_comparison.png` | Box plots | Magnetic/Dynamic/Total pressure across events |
| 21 | `21_hexbin_np_vp_<date>.png` | Hexbin | Density of Np vs Vp per event |
| 22 | `22_vp_step_histogram.png` | Step histograms | Overlaid Vp density per event |
| 23 | `23_lag_plots_<date>.png` | Lag-1 scatter | Memory/turbulence diagnostic per event |
| 24 | `24_ptot_vs_beta_<date>.png` | Log scatter | Total Pressure vs Beta (MC regime) |
| 25 | `25_dashboard_<date>.png` | Multi-panel dashboard | Consolidated 6-panel summary per event |

A `descriptions.txt` file will also be written to the `images/` folder containing every description as text."""))

# =========================================================================
# DESC FILE GENERATOR (writes images/descriptions.txt)
# =========================================================================
cells.append(new_code_cell('''descriptions = """01_multipanel_timeseries.png
  Description: Multi-panel time series of BTOTAL, Np, Vp, Tp, Beta for all 5 events overlaid.
  Shows the overall state of magnetic field and plasma during each event window.

02_bfield_rtn_<date>.png (one per event)
  Description: Time series of the 3 magnetic field RTN components (R, T, N) along with |B|.
  Smooth rotations of B_T/B_N are a signature of magnetic flux rope passage.

03_scatter_np_vp_<date>.png (one per event)
  Description: Scatter of Np vs Vp colored by time progression, with linear regression line.
  In quiet solar wind there is an inverse Np-Vp correlation; ICMEs disrupt it.

04_histograms_all.png
  Description: Probability density histograms for 8 key variables across all events overlaid.
  Useful for spotting bimodality (two solar wind streams) and skewness.

05_corr_heatmap_<date>.png (one per event)
  Description: Pearson correlation matrix. Red=positive correlation, Blue=negative.
  Key pairs: |B|--Beta (anti); Vp--Tp (positive); Np--Np-derived variables.

06_boxplots.png
  Description: Box plots of 8 variables per event. Compare median, IQR, outliers.
  Identifies which event had the most extreme values.

06b_violinplots.png
  Description: Same as box plots but using a KDE width — reveals bimodality and heavy tails
  that box plots might hide.

07_hee_trajectory.png
  Description: 2D spacecraft position in HEE X-Y coordinates (Sun at origin).
  Compares the 1 AU reference orbit with STEREO-A's trajectory.

08_distance_r.png
  Description: Heliocentric distance R over each event. STEREO-A is near 1 AU.
  Small orbital arcs are visible; relevant for plasma interpretation.

09_pressures_<date>.png (one per event)
  Description: Stacked area of magnetic + dynamic pressure, with total overlaid.
  When magnetic pressure dominates, you are likely inside a magnetic cloud.

10_angles_<date>.png (one per event)
  Description: Cone angle (0-180) and Clock angle (-180 to +180) scatter plots colored by |B|.
  Smooth rotations suggest flux-rope signature.

11_kde_vp_tp_<date>.png (one per event)
  Description: Joint 2D KDE estimate of Vp vs Tp with linear fit.
  Reveals the main "cloud" of solar wind state in (Vp, Tp) space.

12_velocity_polar_<date>.png (one per event)
  Description: Polar scatter in the transverse velocity plane (Vt, Vn). Color=Vr/V.
  Radial flow should cluster with Vr/V near 1.

13_beta_vs_btotal_<date>.png (one per event)
  Description: Beta vs |B| (log) colored by Tp. Low-Beta + high-|B| = magnetic cloud (MC) regime.

14_velocity_cosines_<date>.png (one per event)
  Description: Time series of Vr/V, Vt/V, Vn/V. Deviations from Vr/V=1 indicate deflected flow
  at CME shocks/sheaths.

15_pairplot_<date>.png (one per event)
  Description: Pairwise scatter + KDE for BTOTAL/Np/Vp/Tp/Beta. Off-diagonal = joint structure,
  diagonal = marginal distribution.

16_vp_smoothed_<date>.png (one per event)
  Description: Raw vs 1-hour rolling-mean Vp. Highlights HSS regions (Vp > 400 km/s).

17_entropy_beta_<date>.png (one per event)
  Description: Dual-axis time series of Entropy and Beta. Anti-correlation typical of
  hot low-density wind.

18_bfield_3d_<date>.png (one per event)
  Description: 3D scatter of B_R/B_T/B_N colored by |B|. A helical organization = flux rope.

19_autocorrelation_<date>.png (one per event)
  Description: ACF of 5 key variables. Long decay = coherent structure; rapid decay = turbulence.

20_pressure_comparison.png
  Description: Box plots comparing magnetic, dynamic, total pressure across all events.

21_hexbin_np_vp_<date>.png (one per event)
  Description: Hexbin density plot of Np vs Vp. Bright hexes = common wind state.

22_vp_step_histogram.png
  Description: Step-style overlaid histograms of Vp density per event.
  Direct visual comparison of wind speed populations.

23_lag_plots_<date>.png (one per event)
  Description: Lag-1 scatter plots for 5 variables. Diagonal organization indicates memory.

24_ptot_vs_beta_<date>.png (one per event)
  Description: Total Pressure vs Beta (log). MC regime = Beta<1 with elevated Ptot.

25_dashboard_<date>.png (one per event)
  Description: Consolidated 6-panel dashboard per event — quick visual diagnosis.
"""

with open(os.path.join(img_dir, 'descriptions.txt'), 'w') as f:
    f.write(descriptions)

# List all saved files
saved_files = sorted(os.listdir(img_dir))
print(f'Total files in images/: {len(saved_files)}')
for f in saved_files:
    path = os.path.join(img_dir, f)
    size = os.path.getsize(path)
    print(f'  {f} ({size:,} bytes)')
'''))

# Assemble the notebook
nb['cells'] = cells

with open('stereo_visualizations.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'\nNotebook saved with {len(cells)} cells.')
print('Now executing the notebook...')

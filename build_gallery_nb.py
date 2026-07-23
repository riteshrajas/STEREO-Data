"""
Build a Jupyter notebook that generates a wide variety of graph/visualization
types using matplotlib, seaborn, and plotly. Each cell:
  - writes a PNG (matplotlib/seaborn) or interactive HTML (plotly) into images/
  - renders inline in the notebook
  - includes a description of the graph type and what it shows
At the end, the notebook zips all images into visualization_gallery.zip
so the user can download every chart with one file.
"""
import nbformat as nbf
from pathlib import Path

NB_NAME = "P:/laney/visualization_gallery.ipynb"
IMG_DIR = "images"

nb = nbf.v4.new_notebook()
cells = []

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))

def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ---------------- Header ----------------
md(f"""# Visualization Gallery — Every Type of Graph I Could Think Of
Generated on {Path('.').resolve()}.

This notebook builds ~40 different chart/visualization types so you can see,
at a glance, what each one looks like and decide which fits your data. Every
chart is also saved as a PNG into `{IMG_DIR}/` (or HTML for the interactive
plotly ones) and bundled into `visualization_gallery.zip` at the end so you
can download all of them at once.

**Libraries used**: matplotlib, seaborn, plotly (+ numpy / pandas / scipy /
scikit-learn / networkx for datasets).
""")

# ---------------- 0. Setup ----------------
md("## 0 · Setup & shared dataset")
code(f"""# core libs
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')                # headless-safe backend; still inline via %matplotlib inline later
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import networkx as nx
from scipy import stats, ndimage
import warnings, os, zipfile, textwrap
warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({{"figure.dpi": 110, "savefig.dpi": 130, "savefig.bbox": "tight"}})

# headless inline for the notebook
%matplotlib inline

IMG = {IMG_DIR!r}
os.makedirs(IMG, exist_ok=True)
SAVE_OPTS = dict(bbox_inches="tight", dpi=130)

def save(fig, name):
    path = os.path.join(IMG, name + ".png")
    fig.savefig(path, **SAVE_OPTS)
    plt.show()
    print("saved", path)
    return path

# reproducible random data
rng = np.random.default_rng(42)

# shared datasets reused across charts
N = 200
df = pd.DataFrame({{
    "x": rng.normal(0, 1, N),
    "y": 0.7 * np.arange(-N//2, N//2) + rng.normal(0, 4, N),
    "group": rng.choice(["A","B","C","D"], N),
    "value": rng.gamma(2, 2, N),
    "category": rng.choice(["low","med","high"], N),
    "time": pd.date_range("2024-01-01", periods=N, freq="D"),
    "score_A": rng.normal(70, 10, N).clip(0,100),
    "score_B": rng.normal(65, 12, N).clip(0,100),
    "lat": rng.uniform(-90, 90, N),
    "lon": rng.uniform(-180, 180, N),
}})

multi = pd.DataFrame({{
    "Month": list(range(1,13))*4,
    "Year":  np.repeat([2021,2022,2023,2024], 12),
    "Sales": rng.poisson(50 + np.tile(np.arange(12),4)*2, 48),
    "Region": np.tile(["North","South","East","West"], 3) * 4 % 48,
}})
print("Setup done. df shape:", df.shape, "| multi shape:", multi.shape)
""")

# helper to make one chart: markdown + code
def chart(desc_md, code_str):
    md(desc_md)
    code(code_str)

# ---------------- 1. Line chart ----------------
chart("""## 1 · Line chart
Shows how a continuous quantity changes along an ordered axis (usually time).
Best for **trends** over an interval.""",
"""fig, ax = plt.subplots(figsize=(8,4))
ax.plot(df['time'], df['value'], color='steelblue', lw=1.4)
ax.set(title='Daily gamma-distributed value', xlabel='Date', ylabel='Value')
save(fig, "01_line")""")

# ---------------- 2. Multi-line ----------------
chart("""## 2 · Multi-line chart
Multiple series on the same axes to compare **trends across groups**.""",
"""fig, ax = plt.subplots(figsize=(9,4))
for g in ['A','B','C','D']:
    sub = df[df.group==g]
    ax.plot(sub['time'], sub['value'].cumsum(), label=g, lw=1.5, alpha=.8)
ax.set(title='Cumulative value by group', xlabel='Date', ylabel='cumulative')
ax.legend()
save(fig, "02_multi_line")""")

# ---------------- 3. Bar chart ----------------
chart("""## 3 · Bar chart
Compares a **categorical** quantity across discrete groups. Length encodes the value.""",
"""fig, ax = plt.subplots(figsize=(7,4))
df.groupby('group')['value'].mean().plot.bar(ax=ax, color='#4c72b0')
ax.set(title='Mean value by group', ylabel='Mean')
save(fig, "03_bar")""")

# ---------------- 4. Grouped bar ----------------
chart("""## 4 · Grouped bar chart
Bar chart with **sub-bars side-by-side** for each group — compares two categorical dimensions.""",
"""pivot = df.pivot_table(index='group', columns='category', values='value', aggfunc='mean')
fig, ax = plt.subplots(figsize=(8,4))
pivot.plot.bar(ax=ax)
ax.set(title='Mean by group × category', ylabel='mean')
save(fig, "04_grouped_bar")""")

# ---------------- 5. Stacked bar ----------------
chart("""## 5 · Stacked bar chart
Like grouped bar but segments stacked — good when you care about **totals and proportions**.""",
"""fig, ax = plt.subplots(figsize=(8,4))
pivot.plot.bar(stacked=True, ax=ax, colormap='viridis')
ax.set(title='Stacked mean by group × category', ylabel='mean')
save(fig, "05_stacked_bar")""")

# ---------------- 6. 100% stacked bar ----------------
chart("""## 6 · 100% stacked bar
Each bar normalized to 100% — shows **proportional composition** regardless of total size.""",
"""norm = pivot.div(pivot.sum(axis=1), axis=0)
fig, ax = plt.subplots(figsize=(8,4))
norm.plot.bar(stacked=True, ax=ax, colormap='tab10')
ax.set(title='100% stacked (proportions)', ylabel='fraction')
ax.set_ylim(0,1)
save(fig, "06_100pct_stacked_bar")""")

# ---------------- 7. Horizontal bar ----------------
chart("""## 7 · Horizontal bar chart
Bar chart flipped sideways — better when **category labels are long**.""",
"""fig, ax = plt.subplots(figsize=(8,4))
df.groupby('group')['value'].mean().plot.barh(ax=ax, color='#dd8452')
ax.set(title='Mean value (horizontal)', xlabel='mean')
save(fig, "07_horizontal_bar")""")

# ---------------- 8. Histogram ----------------
chart("""## 8 · Histogram
Buckets a continuous variable into bins and counts — shows the **shape of the distribution**.""",
"""fig, ax = plt.subplots(figsize=(7,4))
ax.hist(df['value'], bins=20, color='#55a868', edgecolor='white')
ax.set(title='Histogram of value', xlabel='value', ylabel='count')
save(fig, "08_histogram")""")

# ---------------- 9. Density / KDE ----------------
chart("""## 9 · Kernel density estimate (KDE)
Smooths the histogram into a probability density — useful for comparing **distributions** without bin discretization.""",
"""fig, ax = plt.subplots(figsize=(7,4))
for g in ['A','B','C','D']:
    sns.kdeplot(df[df.group==g]['value'], ax=ax, label=g, fill=True, alpha=.25)
ax.set(title='KDE of value by group')
ax.legend()
save(fig, "09_kde")""")

# ---------------- 10. Box plot ----------------
chart("""## 10 · Box plot (box-and-whisker)
Shows median, IQR, whiskers, and outliers per group — compact **distributional summary**.""",
"""fig, ax = plt.subplots(figsize=(7,4))
sns.boxplot(data=df, x='group', y='value', ax=ax, palette='pastel')
ax.set(title='Box plot of value by group')
save(fig, "10_boxplot")""")

# ---------------- 11. Violin plot ----------------
chart("""## 11 · Violin plot
Box plot + KDE mirrored on each side — shows the **full distribution shape** per category.""",
"""fig, ax = plt.subplots(figsize=(7,4))
sns.violinplot(data=df, x='group', y='value', ax=ax, palette='muted', inner='quartile')
ax.set(title='Violin plot of value by group')
save(fig, "11_violin")""")

# ---------------- 12. Strip / swarm ----------------
chart("""## 12 · Swarm plot
Plots every individual point, jittered so none overlap — **raw points** with category grouping.""",
"""fig, ax = plt.subplots(figsize=(7,4))
sns.swarmplot(data=df.sample(120), x='group', y='value', ax=ax, size=3)
ax.set(title='Swarm plot (every point visible)')
save(fig, "12_swarm")""")

# ---------------- 13. Box + swarm ----------------
chart("""## 13 · Box + swarm overlay
Combines distributional summary with individual points — **points on top of box**.""",
"""fig, ax = plt.subplots(figsize=(7,4))
sns.boxplot(data=df, x='group', y='value', ax=ax, boxprops=dict(alpha=.5))
sns.swarmplot(data=df.sample(120), x='group', y='value', ax=ax, size=2.5, color='.25')
ax.set(title='Box + swarm overlay')
save(fig, "13_box_swarm")""")

# ---------------- 14. Scatter ----------------
chart("""## 14 · Scatter plot
Two continuous variables vs each other — the canonical **correlation view**.""",
"""fig, ax = plt.subplots(figsize=(7,5))
ax.scatter(df['x'], df['y'], c=df['value'], cmap='viridis', s=20, alpha=.75)
ax.set(title='Scatter: y vs x (color=value)', xlabel='x', ylabel='y')
fig.colorbar(ax.collections[0], ax=ax, label='value')
save(fig, "14_scatter")""")

# ---------------- 15. Scatter with regression ----------------
chart("""## 15 · Scatter + regression line
Adds a fitted OLS line + 95% CI — the **trend-with-uncertainty** version of a scatter.""",
"""fig, ax = plt.subplots(figsize=(7,5))
sns.regplot(data=df, x='x', y='y', ax=ax, scatter_kws=dict(s=18, alpha=.6), line_kws=dict(color='crimson'))
ax.set(title='Scatter + linear regression + 95% CI')
save(fig, "15_scatter_regress")""")

# ---------------- 16. Bubble chart ----------------
chart("""## 16 · Bubble chart
Scatter with **marker size encoding a third variable** — three dimensions on a 2D plot.""",
"""fig, ax = plt.subplots(figsize=(7,5))
sc = ax.scatter(df['x'], df['y'], s=df['value']*8, c=df['value'], cmap='plasma', alpha=.6, edgecolor='black', lw=.4)
ax.set(title='Bubble: size=value, color=value')
fig.colorbar(sc, ax=ax, label='value')
save(fig, "16_bubble")""")

# ---------------- 17. Hexbin ----------------
chart("""## 17 · Hexbin plot
Bivariate histogram using hexagonal bins — great for **dense scatter** data.""",
"""fig, ax = plt.subplots(figsize=(7,5))
hb = ax.hexbin(df['x'], df['y'], gridsize=22, cmap='Blues', mincnt=1)
ax.set(title='Hexbin: joint density')
fig.colorbar(hb, ax=ax, label='count')
save(fig, "17_hexbin")""")

# ---------------- 18. 2D histogram ----------------
chart("""## 18 · 2D histogram
Rectangular bivariate histogram — alternative to hexbin for **counting joint occurrences**.""",
"""fig, ax = plt.subplots(figsize=(7,5))
h = ax.hist2d(df['x'], df['y'], bins=25, cmap='YlOrRd')
ax.set(title='2D histogram')
fig.colorbar(h[3], ax=ax, label='count')
save(fig, "18_2d_hist")""")

# ---------------- 19. Joint plot ----------------
chart("""## 19 · Joint plot (seaborn)
Scatter + marginal histograms/KDEs in one figure — **joint & marginal distributions** at once.""",
"""g = sns.jointplot(data=df, x='x', y='y', kind='hex', height=5, cmap='viridis')
g.fig.suptitle('Joint plot (hex) with marginals', y=1.02)
plt.show()
g.fig.savefig(os.path.join(IMG,"19_jointplot.png"), **SAVE_OPTS)
print("saved", os.path.join(IMG,"19_jointplot.png"))""")

# ---------------- 20. Pair plot ----------------
chart("""## 20 · Pair plot (scatter matrix)
All-variable pairwise scatters + diagonal univariate plots — quick **multivariate overview**.""",
"""g = sns.pairplot(df[['x','y','value','score_A','score_B','group']], hue='group', height=1.7, corner=True, plot_kws=dict(s=14, alpha=.6))
g.fig.suptitle('Pair plot colored by group', y=1.02)
plt.show()
g.fig.savefig(os.path.join(IMG,"20_pairplot.png"), **SAVE_OPTS)
print("saved", os.path.join(IMG,"20_pairplot.png"))""")

# ---------------- 21. Heatmap ----------------
chart("""## 21 · Heatmap
Color-coded matrix — best for **2D grids / correlation matrices**.""",
"""corr = df[['x','y','value','score_A','score_B']].corr()
fig, ax = plt.subplots(figsize=(6,5))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax, square=True, fmt='.2f')
ax.set(title='Correlation heatmap')
save(fig, "21_heatmap")""")

# ---------------- 22. Correlation clustermap ----------------
chart("""## 22 · Clustermap (clustered heatmap)
Heatmap reordered by **hierarchical clustering** of rows + cols — groups similar variables.""",
"""cols = ['x','y','value','score_A','score_B']
mat = df[cols].corr().values
g = sns.clustermap(mat, row_labels=cols, col_labels=cols, cmap='vlag', center=0, annot=True, figsize=(6,6))
g.fig.suptitle('Clustered correlation matrix', y=1.03)
plt.show()
g.fig.savefig(os.path.join(IMG,"22_clustermap.png"), **SAVE_OPTS)
print("saved", os.path.join(IMG,"22_clustermap.png"))""")

# ---------------- 23. Pie chart ----------------
chart("""## 23 · Pie chart
Part-to-whole fractions of a single categorical breakdown. Use sparingly — bars are often clearer.""",
"""fig, ax = plt.subplots(figsize=(6,6))
df['group'].value_counts().plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
ax.set(title='Group proportions', ylabel='')
ax.axis('equal')
save(fig, "23_pie")""")

# ---------------- 24. Donut chart ----------------
chart("""## 24 · Donut chart
Pie chart with a hollow center — easier to overlay total / label in the middle.""",
"""fig, ax = plt.subplots(figsize=(6,6))
sizes = df['group'].value_counts()
ax.pie(sizes, labels=sizes.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'),
       wedgeprops=dict(width=0.42, edgecolor='w'))
ax.set(title='Donut: group proportions')
# center label
ax.text(0, 0, f"N={{len(df)}}", ha='center', va='center', fontsize=14, weight='bold')
save(fig, "24_donut")""")

# ---------------- 25. Area chart ----------------
chart("""## 25 · Area chart
Filled line — emphasizes the **cumulative volume** under the curve.""",
"""fig, ax = plt.subplots(figsize=(8,4))
ax.fill_between(df['time'], df['value'], color='#4c72b0', alpha=.5)
ax.set(title='Area chart of value over time', ylabel='value')
save(fig, "25_area")""")

# ---------------- 26. Stacked area ----------------
chart("""## 26 · Stacked area chart
Multiple area series stacked — shows **composition over time** plus totals.""",
"""wide = df.pivot(index='time', columns='group', values='value').fillna(0).rolling(7).mean()
fig, ax = plt.subplots(figsize=(9,4))
ax.stackplot(wide.index, wide.T.values, labels=wide.columns, alpha=.85, cmap='tab10')
ax.set(title='Stacked area by group (7-day rolling)', ylabel='value')
ax.legend(loc='upper left', ncol=4)
save(fig, "26_stacked_area")""")

# ---------------- 27. Step chart ----------------
chart("""## 27 · Step chart
Line drawn as stair-steps — useful when values change **discretely** between points.""",
"""fig, ax = plt.subplots(figsize=(8,4))
ax.step(df['time'][:40], df['value'][:40], where='mid', color='darkgreen', lw=1.6)
ax.set(title='Step chart (discrete changes)')
save(fig, "27_step")""")

# ---------------- 28. Stem plot ----------------
chart("""## 28 · Stem plot
Lines from baseline to each data point — emphasizes **individual discrete samples**.""",
"""fig, ax = plt.subplots(figsize=(8,4))
ax.stem(df['time'][:30], df['value'][:30], basefmt=' ')
ax.set(title='Stem plot')
save(fig, "28_stem")""")

# ---------------- 29. Error bar ----------------
chart("""## 29 · Error bar chart
Bars showing **uncertainty** (±1σ here) around each point — required for honest reporting.""",
"""agg = df.groupby('group')['value'].agg(['mean','std']).reset_index()
fig, ax = plt.subplots(figsize=(7,4))
ax.errorbar(agg['group'], agg['mean'], yerr=agg['std'], fmt='o', color='darkred', capsize=6, lw=2)
ax.set(title='Mean ± 1 std by group', ylabel='mean')
save(fig, "29_errorbar")""")

# ---------------- 30. Radar / spider ----------------
chart("""## 30 · Radar (spider) chart
Multi-axis polygon to compare one entity across several quantitative **metrics at once**.""",
"""metrics = ['speed','power','range','cost','safety']
vals = pd.DataFrame({k: rng.uniform(2,10,4) for k in metrics}, index=['A','B','C','D'])

angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
angles += angles[:1]
fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
for name in vals.index:
    v = vals.loc[name].tolist(); v += v[:1]
    ax.plot(angles, v, label=name, lw=1.6)
    ax.fill(angles, v, alpha=.15)
ax.set_xticks(angles[:-1]); ax.set_xticklabels(metrics)
ax.set_title('Radar: 5-metric comparison', y=1.08)
ax.legend(loc='upper right', bbox_to_anchor=(1.3,1.1))
save(fig, "30_radar")""")

# ---------------- 31. Polar scatter ----------------
chart("""## 31 · Polar scatter
Scatter on polar coordinates — extends scatter when an **angle** is one variable.""",
"""fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
theta = rng.uniform(0, 2*np.pi, 150); r = rng.gamma(2, 1.5, 150)
ax.scatter(theta, r, c=r, cmap='hsv', s=30, alpha=.75)
ax.set_title('Polar scatter', y=1.06)
save(fig, "31_polar_scatter")""")

# ---------------- 32. Contour ----------------
chart("""## 32 · Contour plot
Lines of constant value across two continuous vars — 2D **topographic / level-set** view.""",
"""x = np.linspace(-3, 3, 120); y = np.linspace(-3, 3, 120)
X, Y = np.meshgrid(x, y)
Z = np.sin(X)*np.cos(Y)*np.exp(-(X**2+Y**2)/6)
fig, ax = plt.subplots(figsize=(7,5))
cs = ax.contour(X, Y, Z, 14, cmap='Spectral')
ax.clabel(cs, inline=True, fontsize=8)
ax.set(title='Contour plot', xlabel='x', ylabel='y')
save(fig, "32_contour")""")

# ---------------- 33. Filled contour ----------------
chart("""## 33 · Filled contour (imshow)
Filled version of contour — `contourf` / `imshow` give a smooth **heat-field** view.""",
"""fig, ax = plt.subplots(figsize=(7,5))
cf = ax.contourf(X, Y, Z, 20, cmap='magma')
ax.set(title='Filled contour (contourf)')
fig.colorbar(cf, ax=ax)
save(fig, "33_contourf")""")

# ---------------- 34. Quiver ----------------
chart("""## 34 · Quiver (vector field)
Arrows showing **direction + magnitude** of a 2D vector field — gradient/wind/flow.""",
"""fig, ax = plt.subplots(figsize=(7,6))
xv, yv = np.meshgrid(np.linspace(-2,2,16), np.linspace(-2,2,16))
U = -yv + 0.1*xv; V = xv + 0.1*yv
M = np.hypot(U, V)
ax.quiver(xv, yv, U, V, M, cmap='viridis')
ax.set(title='Quiver: spiral vector field', aspect='equal')
save(fig, "34_quiver")""")

# ---------------- 35. Streamplot ----------------
chart("""## 35 · Streamplot
Continuous flow lines through a vector field — smoother/cleaner than quiver for **trajectories**.""",
"""fig, ax = plt.subplots(figsize=(7,6))
ax.streamplot(xv[0,:], yv[:,0], U, V, color=M, cmap='autumn', density=1.4)
ax.set(title='Streamplot', aspect='equal')
save(fig, "35_streamplot")""")

# ---------------- 36. 3D scatter ----------------
chart("""## 36 · 3D scatter
Three continuous variables — adds **depth** to a normal scatter.""",
"""fig = plt.figure(figsize=(7,6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['x'], df['y'], df['value'], c=df['value'], cmap='turbo', s=20)
ax.set(title='3D scatter', xlabel='x', ylabel='y', zlabel='value')
save(fig, "36_3d_scatter")""")

# ---------------- 37. 3D surface ----------------
chart("""## 37 · 3D surface
A surface in 3-space — best visualization of a **2D function z = f(x,y)**.""",
"""fig = plt.figure(figsize=(7.5,6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='coolwarm', edgecolor='none', alpha=.95)
ax.set(title='3D surface', xlabel='x', ylabel='y', zlabel='z')
save(fig, "37_3d_surface")""")

# ---------------- 38. Wireframe ----------------
chart("""## 38 · 3D wireframe
Wireframe variant of the surface — emphasizes the **mesh structure** without fill.""",
"""fig = plt.figure(figsize=(7.5,6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, Y, Z, color='steelblue', lw=0.6)
ax.set(title='3D wireframe')
save(fig, "38_wireframe")""")

# ---------------- 39. Treemap-ish via squarify (manual fallback) ----------------
chart("""## 39 · Treemap (manual squarify)
Nested rectangles sized by value — communicates **hierarchical proportions** without a bar per leaf.""",
"""# pure-matplotlib treemap — no extra dependency
sizes = df['group'].value_counts().sort_index().values
labels = df['group'].value_counts().sort_index().index.tolist()
norm = sizes / sizes.sum()
# simple slice-and-dice layout
fig, ax = plt.subplots(figsize=(7,5))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
x = 0
for w, lab, n in zip(norm, labels, sizes):
    ax.add_patch(mpatches.Rectangle((x, 0), w, 1, facecolor=sns.color_palette('Set2')[list(labels).index(lab)], ec='white'))
    ax.text(x + w/2, 0.5, f"{{lab}}\\n{{n}}\\n{{w*100:.1f}}%", ha='center', va='center', color='black')
    x += w
ax.set_title('Treemap (group proportions)')
save(fig, "39_treemap")""")

# ---------------- 40. Waffle-style grid ----------------
chart("""## 40 · Waffle-grid chart
Grid of small squares, each = one unit — friendlier than pie for **part-to-whole**.""",
"""fig, ax = plt.subplots(figsize=(7,5))
counts = df['group'].value_counts()
total = counts.sum()
grid = 10  # 10x10
per_cell = total / (grid*grid)
mat = np.zeros((grid, grid))
order = counts.index.tolist()
flat = np.repeat(np.arange(len(order)), (counts.values/per_cell).astype(int))
flat = np.concatenate([flat, np.zeros(grid*grid - len(flat), dtype=int)])
mat = flat.reshape(grid, grid)
cmap = matplotlib.colors.ListedColormap(sns.color_palette('Set2').as_hex()[:len(order)])
ax.imshow(mat, cmap=cmap, vmin=0, vmax=len(order)-1)
for r in range(grid):
    for c in range(grid):
        ax.add_patch(plt.Rectangle((c-0.5, r-0.5), 1, 1, fill=False, edgecolor='white', lw=1))
ax.set_xticks([]); ax.set_yticks([])
ax.set_title('Waffle: 1 cell ≈ {:.1f} samples'.format(per_cell))
handles = [mpatches.Patch(color=sns.color_palette('Set2')[i], label=order[i]) for i in range(len(order))]
ax.legend(handles=handles, bbox_to_anchor=(1.05,1), loc='upper left')
save(fig, "40_waffle")""")

# ---------------- 41. Diverging bar ----------------
chart("""## 41 · Diverging bar chart
Bars extend left/right of center — good for **positive vs negative** quantities (likes/dislikes, deltas).""",
"""diff = df.groupby('group')[['score_A','score_B']].mean().eval('score_A - score_B').sort_values()
fig, ax = plt.subplots(figsize=(8,4))
diff.plot.barh(ax=ax, color=['#c44e52' if v<0 else '#4c72b0' for v in diff.values])
ax.axvline(0, color='black', lw=.8)
ax.set(title='Diverging bar (score_A − score_B)', xlabel='delta')
save(fig, "41_diverging_bar")""")

# ---------------- 42. Calendar / heatmap-of-time ----------------
chart("""## 42 · Calendar heatmap
Time-series as a year × weekday heatmap — embeddings by **date-of-year**.""",
"""ts = pd.Series(rng.poisson(8, 365), index=pd.date_range('2024-01-01', periods=365))
cal = pd.DataFrame({{'value': ts.values, 'month': ts.index.month, 'day': ts.index.day}})
mat = cal.pivot_table(index='month', columns='day', values='value')
fig, ax = plt.subplots(figsize=(11,4))
sns.heatmap(mat, cmap='Greens', ax=ax, cbar_kws=dict(label='count'), xticklabels=5)
ax.set(title='Calendar heatmap of daily counts (2024)')
save(fig, "42_calendar_heatmap")""")

# ---------------- 43. Lag plot ----------------
chart("""## 43 · Lag plot
Value at t vs value at t−k — diagonal pattern reveals **autocorrelation** in a series.""",
"""fig, ax = plt.subplots(figsize=(6,5))
pd.plotting.lag_plot(df['value'], lag=1, ax=ax, c='steelblue', alpha=.6)
ax.set_title('Lag-1 plot (autocorrelation)')
save(fig, "43_lag_plot")""")

# ---------------- 44. Autocorrelation plot ----------------
chart("""## 44 · Autocorrelation plot
Correlation of a series with itself across lags — finds **periodicity / AR structure**.""",
"""fig, ax = plt.subplots(figsize=(8,4))
pd.plotting.autocorrelation_plot(df['value'][:100], ax=ax)
ax.set_title('Autocorrelation')
save(fig, "44_autocorrelation")""")

# ---------------- 45. QQ plot ----------------
chart("""## 45 · Q-Q plot
Sample quantiles vs theoretical normal quantiles — straight line ⇒ **normal distribution**.""",
"""fig, ax = plt.subplots(figsize=(6,5))
stats.probplot(df['value'], dist='norm', plot=ax)
ax.set_title('Normal Q-Q plot')
save(fig, "45_qq")""")

# ---------------- 46. Parallel coordinates ----------------
chart("""## 46 · Parallel coordinates
One line per sample across multiple axes — spot **class clusters across many variables**.""",
"""from pandas.plotting import parallel_coordinates
sample = df[['x','y','value','score_A','score_B','group']].sample(80).copy()
# normalize for comparable axes
norm = sample.copy()
for c in ['x','y','value','score_A','score_B']:
    norm[c] = (sample[c] - sample[c].mean())/sample[c].std()
fig, ax = plt.subplots(figsize=(8,4))
parallel_coordinates(norm, 'group', colormap='tab10', ax=ax, alpha=.5, lw=1)
ax.set_title('Parallel coordinates (normalized)')
ax.legend(loc='upper right', ncol=4)
save(fig, "46_parallel_coordinates")""")

# ---------------- 47. Andrews curve ----------------
chart("""## 47 · Andrews curve
Fourier-basis embedding of each sample's variables — a **smooth multivariate signature** per class.""",
"""from pandas.plotting import andrews_curves
fig, ax = plt.subplots(figsize=(8,4))
andrews_curves(norm, 'group', colormap='tab10', ax=ax, alpha=.5, sample_points=200, lw=1)
ax.set_title('Andrews curves')
save(fig, "47_andrews")""")

# ---------------- 48. Lag matrix / rolling heatmap ----------------
chart("""## 48 · Lag autocorr matrix heatmap
Computed autocorrelation over many lags, displayed as a **horizontal strip heatmap**.""",
"""series = df['value'][:200]
lags = np.arange(0, 50)
ac = [series.autocorr(l) for l in lags]
fig, ax = plt.subplots(figsize=(9,2.5))
im = ax.imshow([ac], cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
ax.set_yticks([0]); ax.set_yticklabels(['ACF'])
ax.set_xticks(lags[::5])
ax.set_title('Autocorrelation across lags 0–49')
fig.colorbar(im, ax=ax, label='ACF')
save(fig, "48_acf_heatmap")""")

# ---------------- 49. Word-cloud substitute (text bars) ----------------
chart("""## 49 · Word frequency bar chart
(Rather than a true word cloud, which needs the wordcloud package.) Bars sized by word **frequency** — text visualization.""",
"""text = ("data visualization matplotlib seaborn plotly pandas numpy graph chart "
         "histogram scatter boxplot violin heatmap line bar pie area contour "
         "radar 3d stream quiver treemap waffle lag autocorrelation qq").split()
words = rng.choice(text, 300)
freq = pd.Series(words).value_counts().head(15)
fig, ax = plt.subplots(figsize=(8,5))
freq.plot.barh(ax=ax, color='#6b6ecf')
ax.invert_yaxis()
ax.set(title='Word frequency (top 15)', xlabel='count')
save(fig, "49_word_freq")""")

# ---------------- 50. Network graph ----------------
chart("""## 50 · Network graph (graph theory)
Nodes + edges drawn as a force-directed layout — visualizes **relationships / topology**.""",
"""G = nx.erdos_renyi_graph(30, 0.12, seed=7)
deg = dict(G.degree())
fig, ax = plt.subplots(figsize=(7,6))
pos = nx.spring_layout(G, seed=7)
nx.draw_networkx_edges(G, pos, ax=ax, alpha=.4)
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[v*80 for v in deg.values()],
                       node_color=list(deg.values()), cmap='plasma')
ax.set_title('Network graph (node color/size = degree)')
ax.axis('off')
save(fig, "50_network")""")

# ---------------- 51. Sankey-ish via matplotlib ----------------
chart("""## 51 · Alluvial / Sankey-style flow (matplotlib)
Two-stage categorical flows; band thickness encodes **how many flow between categories**.""",
"""from matplotlib.path import Path
from matplotlib.patches import PathPatch

left = df['group'].value_counts().sort_index()
right = df['category'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8,5))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
# draw left bars
left_y = 0
left_positions = []
for k, v in left.items():
    ax.add_patch(mpatches.Rectangle((0.08, left_y), 0.06, v/df.shape[0], color=sns.color_palette('pastel')[list(left.index).index(k)]))
    left_positions.append((left_y, left_y + v/df.shape[0]))
    ax.text(0.05, left_y + v/df.shape[0]/2, k, ha='right', va='center')
    left_y += v/df.shape[0] + 0.01
right_y = 0
right_positions = []
for k, v in right.items():
    ax.add_patch(mpatches.Rectangle((0.86, right_y), 0.06, v/df.shape[0], color=sns.color_palette('muted')[list(right.index).index(k)]))
    right_positions.append((right_y, right_y + v/df.shape[0]))
    ax.text(0.96, right_y + v/df.shape[0]/2, k, ha='left', va='center')
    right_y += v/df.shape[0] + 0.01
# flows: simulate even split
for i, (ly0, ly1) in enumerate(left_positions):
    for j, (ry0, ry1) in enumerate(right_positions):
        verts = [(0.14, ly0), (0.5, ly0), (0.5, ry0), (0.86, ry0), (0.86, ry1), (0.5, ry1), (0.5, ly1), (0.14, ly1), (0.14, ly0)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor='gray', alpha=0.15, edgecolor='none'))
ax.set_title('Sankey-style flow: group → category')
save(fig, "51_sankey")""")

# ---------------- 52. Sparkline strip ----------------
chart("""## 52 · Sparkline strip
Tiny per-group line charts in a row — **compact trend comparison**.""",
"""fig, axes = plt.subplots(1, 4, figsize=(11,2.2))
for ax, g in zip(axes, ['A','B','C','D']):
    sub = df[df.group==g]['value'].rolling(7).mean()
    ax.plot(sub.values, color='steelblue', lw=1.3)
    ax.fill_between(range(len(sub)), sub.values, alpha=.25, color='steelblue')
    ax.set_title(f'Group {{g}}', fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle('Sparkline strip (7-day rolling mean per group)', y=1.05)
save(fig, "52_sparklines")""")

# ---------------- 53. Ridge plot ----------------
chart("""## 53 · Ridge (joy) plot
Overlapping KDEs stacked vertically — compare **distributions across many groups** at once.""",
"""fig, ax = plt.subplots(figsize=(7,5))
groups = ['A','B','C','D']
for i, g in enumerate(groups):
    sub = df[df.group==g]['value']
    dens = np.linspace(sub.min(), sub.max(), 100)
    kde = stats.gaussian_kde(sub)
    y = kde(dens)
    y = y / y.max() * 0.8
    ax.fill_between(dens, i, i + y, color=sns.color_palette('crest')[i], alpha=.8)
    ax.plot(dens, i + y, color='black', lw=.5)
ax.set_yticks(np.arange(len(groups))); ax.set_yticklabels(groups)
ax.set(title='Ridge plot (KDE ridges per group)', xlabel='value')
save(fig, "53_ridge")""")

# ---------------- 54. Reaction / venn ----------------
chart("""## 54 · Venn-style 2-set overlap (matplotlib)
Two overlapping circles — when both categorical **membership sets intersect**.""",
"""import matplotlib.patches as mp
fig, ax = plt.subplots(figsize=(6,5))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal'); ax.axis('off')
c1 = mp.Circle((0.4,0.5), 0.3, color='#4c72b0', alpha=.6)
c2 = mp.Circle((0.6,0.5), 0.3, color='#dd8452', alpha=.6)
ax.add_patch(c1); ax.add_patch(c2)
ax.text(0.30, 0.5, 'A\\nonly', ha='center', va='center', color='white', fontsize=11)
ax.text(0.70, 0.5, 'B\\nonly', ha='center', va='center', color='white', fontsize=11)
ax.text(0.50, 0.5, 'A∩B', ha='center', va='center', fontsize=11)
ax.set_title('Two-set Venn (overlap)')
save(fig, "54_venn")""")

# ---------------- 55. Plotly interactive (html) ----------------
chart("""## 55 · Plotly interactive scatter (HTML)
Plotly charts are interactive: hover, zoom, pan, export. Saved as standalone HTML in `images/`.""",
"""import plotly.express as px
figp = px.scatter(df.head(150), x='x', y='y', color='group', size='value', hover_data=['time'])
figp.update_layout(title='Plotly interactive scatter', template='plotly_white')
plotly_path_html = os.path.join(IMG, "55_plotly_scatter.html")
figp.write_html(plotly_path_html, include_plotlyjs=True)
# also try a static png via kaleido (optional; fail silently)
try:
    figp.write_image(os.path.join(IMG,"55_plotly_scatter.png"), scale=1.3, width=800, height=500)
    print("saved PNG", os.path.join(IMG,"55_plotly_scatter.png"))
except Exception as e:
    print("plotly png skipped:", e)
print("saved interactive HTML", plotly_path_html)
figp.show()""")

# ---------------- 56. Plotly 3D interactive ----------------
chart("""## 56 · Plotly 3D scatter (HTML) + PNG
Rotatable 3D scatter — true interactivity for **3 numeric axes**.""",
"""figp3 = px.scatter_3d(df.head(200), x='x', y='y', z='value', color='group')
figp3.update_layout(title='Plotly 3D scatter', template='plotly_white', margin=dict(l=0,r=0,b=0,t=40))
plotly_path_html3 = os.path.join(IMG, "56_plotly_3d.html")
figp3.write_html(plotly_path_html3, include_plotlyjs=True)
try:
    figp3.write_image(os.path.join(IMG,"56_plotly_3d.png"), scale=1.3, width=800, height=600)
    print("saved PNG", os.path.join(IMG,"56_plotly_3d.png"))
except Exception as e:
    print("plotly png skipped:", e)
print("saved interactive HTML", plotly_path_html3)
figp3.show()""")

# ---------------- 57. Funnel chart ----------------
chart("""## 57 · Plotly funnel chart
Stage-by-stage conversion — each segment is **narrower than the last**.""",
"""stages = ['Visited','Signed up','Activated','Subscribed','Renewed']
vals = [1000, 620, 410, 180, 120]
figf = px.funnel(x=vals, y=stages, title='Conversion funnel')
figf.update_layout(template='plotly_white')
funnel_html = os.path.join(IMG, "57_plotly_funnel.html")
figf.write_html(funnel_html, include_plotlyjs=True)
try:
    figf.write_image(os.path.join(IMG,"57_plotly_funnel.png"), scale=1.3, width=700, height=450)
    print("saved PNG", os.path.join(IMG,"57_plotly_funnel.png"))
except Exception as e:
    print("plotly png skipped:", e)
print("saved interactive HTML", funnel_html)
figf.show()""")

# ---------------- 58. Timeline / Gantt-ish ----------------
chart("""## 58 · Timeline / Gantt-style bars
Horizontal bars with start/end spans — for **durations / events over time**.""",
"""import matplotlib.dates as mdates
events = [('Event 1','2024-01-15','2024-02-10'),
          ('Event 2','2024-02-05','2024-03-20'),
          ('Event 3','2024-03-15','2024-04-25'),
          ('Event 4','2024-04-20','2024-06-15')]
fig, ax = plt.subplots(figsize=(9,4))
for i,(name,s,e) in enumerate(events):
    start = pd.Timestamp(s); end = pd.Timestamp(e)
    ax.barh(i, (end-start).days, left=start, height=0.5, color=sns.color_palette('tab10')[i])
    ax.text(start, i, ' '+name, va='center', fontsize=9)
ax.set_yticks([]); ax.invert_yaxis()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set(title='Timeline / Gantt-style chart', xlabel='2024')
save(fig, "58_timeline")""")

# ---------------- 59. Polar bar ----------------
chart("""## 59 · Polar bar (rose) chart
Bar chart on a polar axis — encodes direction + magnitude (e.g. wind direction).""",
"""fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(projection='polar'))
dirs = np.linspace(0, 2*np.pi, 16, endpoint=False)
vals = rng.gamma(2, 2, 16)
ax.bar(dirs, vals, width=2*np.pi/16, color=sns.color_palette('husl', 16), edgecolor='white')
ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
ax.set_title('Polar bar (rose) chart', y=1.08)
save(fig, "59_polar_bar")""")

# ---------------- 60. Mosaic / mosaicplot via heatmap ----------------
chart("""## 60 · Mosaic plot (2-way contingency heatmap)
Counts of two categorical variables coloured by standardized residual — **cell-level significance**.""",
"""ct = pd.crosstab(df['group'], df['category'])
fig, ax = plt.subplots(figsize=(7,4))
sns.heatmap(ct, annot=True, fmt='d', cmap='YlGnBu', ax=ax, cbar_kws=dict(label='count'))
ax.set(title='Mosaic / contingency heatmap: group × category', xlabel='category', ylabel='group')
save(fig, "60_mosaic")""")

# ---------------- 61. Decision tree (sklearn) ----------------
chart("""## 61 · Decision tree (sklearn plot_tree)
Tree visualization of a small classifier — **flowchart of decisions**.""",
"""from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import load_iris
iris = load_iris()
clf = DecisionTreeClassifier(max_depth=3, random_state=0).fit(iris.data, iris.target)
fig, ax = plt.subplots(figsize=(11,6))
plot_tree(clf, feature_names=iris.feature_names, class_names=iris.target_names,
          filled=True, rounded=True, ax=ax, fontsize=9)
ax.set_title('Decision tree (depth 3, iris)')
save(fig, "61_decision_tree")""")

# ---------------- 62. ROC curve ----------------
chart("""## 62 · ROC curve
TPR vs FPR — measuring **binary classifier quality**; AUC summarizes it.""",
"""from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
Xb, yb = make_classification(n_samples=400, n_features=5, weights=[0.7], random_state=1)
clf = LogisticRegression(max_iter=200).fit(Xb, yb)
proba = clf.predict_proba(Xb)[:,1]
fpr, tpr, _ = roc_curve(yb, proba)
roc_auc = auc(fpr, tpr)
fig, ax = plt.subplots(figsize=(6,6))
ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {{roc_auc:.3f}}')
ax.plot([0,1],[0,1], color='navy', lw=1, linestyle='--', label='random')
ax.set(title='ROC curve', xlabel='FPR', ylabel='TPR', xlim=[0,1], ylim=[0,1])
ax.legend(loc='lower right')
save(fig, "62_roc")""")

# ---------------- 63. Confusion matrix ----------------
chart("""## 63 · Confusion matrix heatmap
Counts of predicted vs actual labels — quick **per-class error** breakdown.""",
"""from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
yb_pred = clf.predict(Xb)
cm = confusion_matrix(yb, yb_pred)
fig, ax = plt.subplots(figsize=(5,5))
ConfusionMatrixDisplay(cm).plot(ax=ax, cmap='Blues', colorbar=False)
ax.set_title('Confusion matrix')
save(fig, "63_confusion_matrix")""")

# ---------------- 64. Residual plot ----------------
chart("""## 64 · Residual plot
Residuals vs fitted — checks **regression assumptions** (random scatter ⇒ good).""",
"""from sklearn.linear_model import LinearRegression
X = df[['x']].values; y = df['y'].values
reg = LinearRegression().fit(X, y)
pred = reg.predict(X); resid = y - pred
fig, ax = plt.subplots(figsize=(7,4))
ax.scatter(pred, resid, s=15, alpha=.7, color='#55a868')
ax.axhline(0, color='black', lw=1)
ax.set(title='Residual plot', xlabel='fitted', ylabel='residual')
save(fig, "64_residual")""")

# ---------------- 65. PDF/CDF ----------------
chart("""## 65 · PDF & CDF
Probability density function and cumulative distribution **overlay** — distribution shape + accumulation.""",
"""x = np.linspace(df['value'].min(), df['value'].max(), 300)
kde = stats.gaussian_kde(df['value'])
pdf = kde(x); cdf = np.cumsum(pdf); cdf /= cdf.max()
fig, ax1 = plt.subplots(figsize=(8,4))
ax1.plot(x, pdf, color='steelblue', label='PDF')
ax1.set_ylabel('PDF', color='steelblue')
ax2 = ax1.twinx()
ax2.plot(x, cdf, color='crimson', label='CDF')
ax2.set_ylabel('CDF', color='crimson')
ax1.set(title='PDF & CDF of value', xlabel='value')
save(fig, "65_pdf_cdf")""")

# ---------------- 66. ECDF ----------------
chart("""## 66 · Empirical CDF (ECDF)
Observed cumulative fraction — **no distribution assumption** about shape.""",
"""fig, ax = plt.subplots(figsize=(7,4))
sns.ecdfplot(data=df, x='value', hue='group', ax=ax)
ax.set(title='Empirical CDF by group')
save(fig, "66_ecdf")""")

# ---------------- 67. Function plot family ----------------
chart("""## 67 · Multiple-function overlay
Several mathematical functions on one axis — **comparative shapes**.""",
"""x = np.linspace(-2*np.pi, 2*np.pi, 400)
fig, ax = plt.subplots(figsize=(8,4))
for f, lab in [(np.sin,'sin'),(np.cos,'cos'),(lambda t: np.sin(t)+0.5*np.cos(2*t),'sin+0.5cos2')]:
    ax.plot(x, f(x), label=lab, lw=1.6)
ax.axhline(0, color='black', lw=.5)
ax.set(title='Function overlays', xlabel='x')
ax.legend()
save(fig, "67_functions")""")

# ---------------- 68. Subplots montage ----------------
chart("""## 68 · Subplot montage
Several chart types side-by-side — **dashboard-style multi-panel**.""",
"""fig, axes = plt.subplots(2, 3, figsize=(13,7))
axes = axes.ravel()
df.groupby('group')['value'].mean().plot.bar(ax=axes[0]); axes[0].set_title('Bar')
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)
axes[1].hist(df['value'], bins=20, color='coral'); axes[1].set_title('Histogram')
axes[2].scatter(df['x'], df['y'], s=10, alpha=.6); axes[2].set_title('Scatter')
df['value'].rolling(20).mean().plot(ax=axes[3], color='darkgreen'); axes[3].set_title('Rolling mean')
sns.boxplot(data=df, x='group', y='value', ax=axes[4]); axes[4].set_title('Boxplot')
axes[5].plot(df['x'][:50], df['value'][:50], marker='o', lw=.5, ms=4); axes[5].set_title('Line')
fig.suptitle('Subplot montage', y=1.02)
fig.tight_layout()
save(fig, "68_subplots")""")

# ---------------- FINAL: zip everything ----------------
md("""## Finally · Zip everything for download
Every chart above was also written to `images/`. This last cell bundles ALL of them
(PNGs + interactive HTMLs) into `visualization_gallery.zip` so you can download the
whole gallery at once.""")

code("""import os, zipfile
zip_path = "visualization_gallery.zip"
count = 0
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(IMG)):
        fp = os.path.join(IMG, fn)
        if os.path.isfile(fp):
            z.write(fp, arcname=os.path.join("visualization_gallery", fn))
            count += 1
print(f"Wrote {{zip_path}} with {{count}} files.")
print("Includes:")
print("\\n".join(f"  {{fn}}" for fn in sorted(os.listdir(IMG))))
""")

md(f"""### Done ✅
Open `visualization_gallery.zip` to grab every chart. Each PNG has a matching
description above (the cell just before its code generates it). For the
plotly charts (cells 55–57), also open the saved `.html` files in a browser
to use the interactive hover/zoom/rotate.
""")

# ---------------- Write notebook ----------------
nb['cells'] = cells
nb['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                 'language_info': {'name': 'python', 'version': '3'}}

with open(NB_NAME, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("wrote", NB_NAME, "with", len(cells), "cells")

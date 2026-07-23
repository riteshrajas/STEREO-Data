"""
Superposed Epoch Analysis — STEREO A & B
Each event gets its own output folder under ./epoch_plots/
Each folder contains 4 panel PNG files:
  1. |B| — total field magnitude
  2. B components (BR, BT, BN) — all on one plot
  3. Solar wind speed (Vp)
  4. Proton density (Np)
Each panel has the event onset centred with a vertical dashed line.
Stats (max, mean, std) are printed and saved as a CSV per event.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cdflib

warnings.filterwarnings("ignore")

# ── Output root ──────────────────────────────────────────────────────────────
OUT_ROOT = r"P:\laney\epoch_plots"
os.makedirs(OUT_ROOT, exist_ok=True)

# ── Window around onset (hours before / after) ────────────────────────────────
HOURS_BEFORE = 48
HOURS_AFTER  = 48

# ── Event definitions ─────────────────────────────────────────────────────────
# (label, onset datetime str, CDF path, spacecraft tag)
EVENTS = [
    {
        "label":    "2010-08-31",
        "onset":    "2010-08-31 00:00",
        "cdf":      r"P:\laney\STEREO_A_Events\Event_2010-08-31\sta_l2_magplasma_1m_20100101_v07.cdf",
        "sc":       "STEREO-A",
    },
    {
        "label":    "2010-10-20",
        "onset":    "2010-10-20 00:00",
        "cdf":      r"P:\laney\STEREO_A_Events\Event_2010-10-20\sta_l2_magplasma_1m_20100101_v07.cdf",
        "sc":       "STEREO-A",
    },
    {
        "label":    "2010-11-02",
        "onset":    "2010-11-02 00:00",
        "cdf":      r"P:\laney\STEREO_A_Events\Event_2010-11-02\sta_l2_magplasma_1m_20100101_v07.cdf",
        "sc":       "STEREO-A",
    },
    {
        "label":    "2010-11-11",
        "onset":    "2010-11-11 00:00",
        "cdf":      r"P:\laney\STEREO_A_Events\STEREO_B_Events\Event_2010-11-11\stb_l2_magplasma_1m_20100101_v07.cdf",
        "sc":       "STEREO-B",
    },
    {
        "label":    "2011-01-21",
        "onset":    "2011-01-21 00:00",
        "cdf":      r"P:\laney\STEREO_A_Events\STEREO_B_Events\Event_2011-01-21\stb_l2_magplasma_1m_20110101_v07.cdf",
        "sc":       "STEREO-B",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_cdf_window(cdf_path: str, onset: pd.Timestamp, hours_before: int, hours_after: int) -> pd.DataFrame:
    """Load CDF, clip to window, return DataFrame with columns:
    Time, BR, BT, BN, BTOTAL, Np, Vp
    """
    c = cdflib.CDF(cdf_path)
    epochs = c.varget("Epoch")
    times_raw = cdflib.cdfepoch.to_datetime(epochs)
    # to_datetime may return list or array of np.datetime64
    times = pd.DatetimeIndex(np.asarray(times_raw, dtype="datetime64[ns]"))

    t_start = onset - pd.Timedelta(hours=hours_before)
    t_end   = onset + pd.Timedelta(hours=hours_after)
    mask = (times >= t_start) & (times <= t_end)
    times_win = times[mask]

    bfield = c.varget("BFIELDRTN")[mask]   # shape (N, 3) — R, T, N
    btotal = c.varget("BTOTAL")[mask]
    np_    = c.varget("Np")[mask]
    vp_    = c.varget("Vp")[mask]

    df = pd.DataFrame({
        "Time":   times_win,
        "BR":     bfield[:, 0],
        "BT":     bfield[:, 1],
        "BN":     bfield[:, 2],
        "BTOTAL": btotal,
        "Np":     np_,
        "Vp":     vp_,
    })

    # Replace fill values (large positives) with NaN
    fill_threshold = 1e29
    for col in ["BR","BT","BN","BTOTAL","Np","Vp"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[np.abs(df[col]) > fill_threshold, col] = np.nan

    df = df.set_index("Time")
    return df


def fmt_stats(series: pd.Series, label: str) -> dict:
    s = series.dropna()
    return {
        "variable": label,
        "max":      round(float(s.max()), 4),
        "mean":     round(float(s.mean()), 4),
        "std":      round(float(s.std()), 4),
        "min":      round(float(s.min()), 4),
    }


def panel_style(ax, onset, ylabel, title, color="steelblue"):
    """Common styling for a single-variable panel."""
    ax.axvline(onset, color="crimson", linewidth=1.5, linestyle="--", label="Onset", zorder=5)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(ax.get_xticklabels(), fontsize=8)
    ax.grid(True, alpha=0.3, linestyle=":")
    ax.spines[["top","right"]].set_visible(False)


def plot_and_save(df: pd.DataFrame, event: dict, out_dir: str):
    onset = pd.Timestamp(event["onset"])
    sc    = event["sc"]
    label = event["label"]

    plt.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "font.size": 10,
    })

    # ── 1. |B| total field ────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(df.index, df["BTOTAL"], color="navy", linewidth=0.9, label="|B|")
    panel_style(ax, onset, "|B| (nT)", f"{sc}  {label}  —  |B| Total Field")
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "01_B_total.png"))
    plt.close(fig)
    print(f"  saved 01_B_total.png")

    # ── 2. B components (BR, BT, BN) on one plot ─────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df.index, df["BR"], color="#E63946", linewidth=0.9, label="B$_R$")
    ax.plot(df.index, df["BT"], color="#2A9D8F", linewidth=0.9, label="B$_T$")
    ax.plot(df.index, df["BN"], color="#E9C46A", linewidth=0.9, label="B$_N$")
    ax.axhline(0, color="k", linewidth=0.4, linestyle="-", alpha=0.5)
    panel_style(ax, onset, "B (nT)", f"{sc}  {label}  —  B Components (RTN)")
    ax.legend(fontsize=9, loc="upper right", ncol=3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "02_B_components.png"))
    plt.close(fig)
    print(f"  saved 02_B_components.png")

    # ── 3. Solar wind speed ───────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(df.index, df["Vp"], color="#2196F3", linewidth=0.9, label="V$_p$")
    panel_style(ax, onset, "Vp (km/s)", f"{sc}  {label}  —  Solar Wind Speed")
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "03_Vp.png"))
    plt.close(fig)
    print(f"  saved 03_Vp.png")

    # ── 4. Proton density ─────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(df.index, df["Np"], color="#FF9800", linewidth=0.9, label="N$_p$")
    panel_style(ax, onset, "Np (cm⁻³)", f"{sc}  {label}  —  Proton Density")
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "04_Np.png"))
    plt.close(fig)
    print(f"  saved 04_Np.png")

    # ── 5. Combined 4-panel overview ──────────────────────────────────────────
    fig, axes = plt.subplots(4, 1, figsize=(13, 14), sharex=True)
    fig.suptitle(
        f"{sc}  |  Event onset: {label}  |  ±{HOURS_BEFORE} h window",
        fontsize=14, fontweight="bold", y=1.01
    )

    # Panel 1 — |B|
    axes[0].plot(df.index, df["BTOTAL"], color="navy", linewidth=0.9, label="|B|")
    axes[0].set_ylabel("|B| (nT)", fontsize=11)
    axes[0].set_title("|B| Total Field", fontsize=11, pad=4)

    # Panel 2 — components
    axes[1].plot(df.index, df["BR"], color="#E63946", linewidth=0.9, label="B$_R$")
    axes[1].plot(df.index, df["BT"], color="#2A9D8F", linewidth=0.9, label="B$_T$")
    axes[1].plot(df.index, df["BN"], color="#E9C46A", linewidth=0.9, label="B$_N$")
    axes[1].axhline(0, color="k", linewidth=0.4, alpha=0.5)
    axes[1].set_ylabel("B (nT)", fontsize=11)
    axes[1].set_title("B Components (RTN)", fontsize=11, pad=4)
    axes[1].legend(fontsize=9, loc="upper right", ncol=3)

    # Panel 3 — Vp
    axes[2].plot(df.index, df["Vp"], color="#2196F3", linewidth=0.9, label="V$_p$")
    axes[2].set_ylabel("Vp (km/s)", fontsize=11)
    axes[2].set_title("Solar Wind Speed", fontsize=11, pad=4)

    # Panel 4 — Np
    axes[3].plot(df.index, df["Np"], color="#FF9800", linewidth=0.9, label="N$_p$")
    axes[3].set_ylabel("Np (cm⁻³)", fontsize=11)
    axes[3].set_title("Proton Density", fontsize=11, pad=4)

    for ax in axes:
        ax.axvline(onset, color="crimson", linewidth=1.8, linestyle="--",
                   label="Onset" if ax == axes[0] else "", zorder=5)
        ax.grid(True, alpha=0.3, linestyle=":")
        ax.spines[["top","right"]].set_visible(False)
        ax.legend(fontsize=9, loc="upper right")

    axes[0].legend(fontsize=9, loc="upper right",
                   handles=axes[0].lines + [matplotlib.lines.Line2D(
                       [], [], color="crimson", linestyle="--", label="Onset")])

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M"))
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(axes[-1].get_xticklabels(), fontsize=8)
    axes[-1].set_xlabel("Time (UT)", fontsize=11)

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "00_overview_4panel.png"))
    plt.close(fig)
    print(f"  saved 00_overview_4panel.png")


def compute_stats(df: pd.DataFrame, event: dict, out_dir: str) -> pd.DataFrame:
    rows = [
        fmt_stats(df["BTOTAL"], "|B| (nT)"),
        fmt_stats(df["BR"],     "BR (nT)"),
        fmt_stats(df["BT"],     "BT (nT)"),
        fmt_stats(df["BN"],     "BN (nT)"),
        fmt_stats(df["Vp"],     "Vp (km/s)"),
        fmt_stats(df["Np"],     "Np (cm⁻³)"),
    ]
    stats_df = pd.DataFrame(rows).set_index("variable")

    csv_path = os.path.join(out_dir, "stats.csv")
    stats_df.to_csv(csv_path)

    print(f"\n  ── Stats for {event['sc']} {event['label']} ──")
    print(stats_df.to_string())
    print()
    return stats_df


# ── Main loop ─────────────────────────────────────────────────────────────────
import matplotlib.lines   # needed for legend handle above

all_stats = {}

for ev in EVENTS:
    print(f"\n{'='*60}")
    print(f"Processing  {ev['sc']}  |  onset {ev['onset']}")
    print(f"{'='*60}")

    out_dir = os.path.join(OUT_ROOT, f"{ev['sc'].replace('-','')}_Event_{ev['label']}")
    os.makedirs(out_dir, exist_ok=True)

    onset = pd.Timestamp(ev["onset"])
    df = load_cdf_window(ev["cdf"], onset, HOURS_BEFORE, HOURS_AFTER)
    print(f"  Loaded {len(df):,} rows  ({df.index[0]} → {df.index[-1]})")

    plot_and_save(df, ev, out_dir)
    stats = compute_stats(df, ev, out_dir)
    all_stats[f"{ev['sc']}_{ev['label']}"] = stats

# ── Summary stats across all events ──────────────────────────────────────────
print(f"\n{'='*60}")
print("COMBINED STATS SUMMARY")
print(f"{'='*60}")
for key, st in all_stats.items():
    print(f"\n{key}")
    print(st.to_string())

# Save combined to root
combined = pd.concat(all_stats, axis=0)
combined.index.names = ["event", "variable"]
combined.to_csv(os.path.join(OUT_ROOT, "all_events_stats.csv"))
print(f"\nSaved combined stats → {os.path.join(OUT_ROOT, 'all_events_stats.csv')}")
print("\nDone.")

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "sep_driver_outputs"
OUT.mkdir(exist_ok=True)

EVENTS = [
    ("STEREO-A", "2010-08-31", ROOT / "STEREO_A_Events" / "Event_2010-08-31" / "STEREO_A_Event_2010-08-31.csv"),
    ("STEREO-A", "2010-10-20", ROOT / "STEREO_A_Events" / "Event_2010-10-20" / "STEREO_A_Event_2010-10-20.csv"),
    ("STEREO-A", "2010-11-02", ROOT / "STEREO_A_Events" / "Event_2010-11-02" / "STEREO_A_Event_2010-11-02.csv"),
    ("STEREO-B", "2010-11-11", ROOT / "STEREO_A_Events" / "STEREO_B_Events" / "Event_2010-11-11" / "STEREO_B_Event_2010-11-11.csv"),
    ("STEREO-B", "2011-01-21", ROOT / "STEREO_A_Events" / "STEREO_B_Events" / "Event_2011-01-21" / "STEREO_B_Event_2011-01-21.csv"),
]


def load_event(spacecraft: str, event_date: str, path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"BTotal": "BTOTAL"})
    df["Time"] = pd.to_datetime(df["Time"])
    df["spacecraft"] = spacecraft
    df["event"] = event_date
    onset = pd.Timestamp(event_date)
    df["epoch_hours"] = (df["Time"] - onset).dt.total_seconds() / 3600.0

    for col in df.columns:
        if col in {"Time", "spacecraft", "event"}:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if pd.api.types.is_numeric_dtype(df[col]):
            df.loc[df[col].abs() > 1e29, col] = np.nan
            df.loc[df[col] < -1e29, col] = np.nan

    # Some A-event files include RTN vector columns; derive magnitude checks where possible.
    if {"BField_R", "BField_T", "BField_N"}.issubset(df.columns):
        df["B_component_sigma"] = df[["BField_R", "BField_T", "BField_N"]].std(axis=1)

    return df


def robust_mean(series: pd.Series) -> float:
    return float(series.dropna().mean()) if series.notna().any() else np.nan


def event_metrics(df: pd.DataFrame) -> dict:
    event = df["event"].iloc[0]
    spacecraft = df["spacecraft"].iloc[0]
    row = {"spacecraft": spacecraft, "event": event}

    pre = df[(df["epoch_hours"] >= -24) & (df["epoch_hours"] < 0)]
    post = df[(df["epoch_hours"] >= 0) & (df["epoch_hours"] <= 24)]
    near = df[(df["epoch_hours"] >= -6) & (df["epoch_hours"] <= 18)]

    variables = [
        "BTOTAL",
        "Vp",
        "Np",
        "Tp",
        "Beta",
        "Entropy",
        "Total_Pressure",
        "Magnetic_Pressure",
        "Dynamic_Pressure",
    ]
    for var in variables:
        if var not in df.columns:
            continue
        pre_mean = robust_mean(pre[var])
        post_mean = robust_mean(post[var])
        row[f"{var}_pre24_mean"] = pre_mean
        row[f"{var}_post24_mean"] = post_mean
        row[f"{var}_post_minus_pre"] = post_mean - pre_mean
        row[f"{var}_post_over_pre"] = post_mean / pre_mean if pre_mean and not np.isnan(pre_mean) else np.nan
        row[f"{var}_near_peak"] = float(near[var].max(skipna=True))
        if near[var].notna().any():
            peak_idx = near[var].idxmax()
            row[f"{var}_peak_epoch_hours"] = float(df.loc[peak_idx, "epoch_hours"])

    if "Vp" in df.columns:
        hourly = df.set_index("Time")["Vp"].resample("1h").median().interpolate(limit=3)
        accel = hourly.diff()
        window = accel[(accel.index >= pd.Timestamp(event) - pd.Timedelta(hours=12)) & (accel.index <= pd.Timestamp(event) + pd.Timedelta(hours=24))]
        row["max_hourly_dVp_km_s"] = float(window.max(skipna=True))
        if window.notna().any():
            row["max_hourly_dVp_epoch_hours"] = float((window.idxmax() - pd.Timestamp(event)).total_seconds() / 3600.0)

    return row


def correlation_table(df: pd.DataFrame, variables: list[str], suffix: str) -> pd.DataFrame:
    available = [v for v in variables if v in df.columns]
    corr = df[available].corr(method="spearman", min_periods=30)
    corr.to_csv(OUT / f"spearman_correlations_{suffix}.csv")
    return corr


def top_pairs(corr: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    rows = []
    cols = list(corr.columns)
    for i, left in enumerate(cols):
        for right in cols[i + 1 :]:
            value = corr.loc[left, right]
            if pd.notna(value):
                rows.append({"left": left, "right": right, "spearman_r": value, "abs_r": abs(value)})
    return pd.DataFrame(rows).sort_values("abs_r", ascending=False).head(n)


def main() -> None:
    frames = [load_event(sc, date, path) for sc, date, path in EVENTS]
    all_data = pd.concat(frames, ignore_index=True, sort=False)
    all_data.to_csv(OUT / "normalized_event_data.csv", index=False)

    metrics = pd.DataFrame([event_metrics(df) for df in frames])
    metrics.to_csv(OUT / "event_before_after_metrics.csv", index=False)

    common_vars = ["BTOTAL", "Vp", "Np", "Tp", "Beta", "Entropy", "Total_Pressure"]
    extended_vars = common_vars + ["Magnetic_Pressure", "Dynamic_Pressure", "B_component_sigma"]

    pooled = all_data[(all_data["epoch_hours"] >= -48) & (all_data["epoch_hours"] <= 48)]
    pooled_corr = correlation_table(pooled, common_vars, "pooled_common")
    a_corr = correlation_table(pooled[pooled["spacecraft"] == "STEREO-A"], extended_vars, "stereo_a_extended")

    top_common = top_pairs(pooled_corr)
    top_a = top_pairs(a_corr)
    top_common.to_csv(OUT / "top_correlations_pooled_common.csv", index=False)
    top_a.to_csv(OUT / "top_correlations_stereo_a_extended.csv", index=False)

    lines = [
        "# SEP Driver Analysis",
        "",
        "This uses the local STEREO event CSVs and aligns each event to 00:00 UT on the listed event date.",
        "It tests plasma and magnetic-field context around the event. It does not include direct SEP particle flux/intensity, so it cannot by itself prove the particle acceleration mechanism.",
        "",
        "## Main Finding",
        "",
        "The clearest in-situ signature in these files is compression and disturbed solar-wind structure near the events: enhanced magnetic-field magnitude, elevated or changing solar-wind speed, density/pressure changes, and low-beta or pressure changes where those columns exist. That pattern is consistent with CME/shock or compressed interaction-region conditions, which are standard environments for SEP acceleration.",
        "",
        "## Strongest Pooled Correlations",
        "",
        top_common[["left", "right", "spearman_r"]].to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Strongest STEREO-A Extended Correlations",
        "",
        top_a[["left", "right", "spearman_r"]].to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Before/After Metrics",
        "",
        metrics.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation",
        "",
        "- If the research question is 'why do SEPs accelerate?', the likely physical answer is not simply high solar-wind speed alone. SEPs are accelerated mainly by shocks and reconnecting/disturbed magnetic structures that provide scattering, compression, and repeated energization.",
        "- In this dataset, useful proxies for those conditions are BTOTAL, Vp jumps, Np, Total_Pressure, Dynamic_Pressure, Magnetic_Pressure, Beta, and field-component variability.",
        "- Correlation is not causation. To argue causation, add SEP intensity/onset profiles, CME/flare timing, shock arrival markers, and magnetic connectivity to the spacecraft.",
        "- The two STEREO-B CSVs have fewer variables than the STEREO-A CSVs, so pressure and magnetic-pressure conclusions mostly come from STEREO-A.",
        "",
    ]
    report = "\n".join(lines)
    (OUT / "sep_driver_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote outputs to: {OUT}")


if __name__ == "__main__":
    main()

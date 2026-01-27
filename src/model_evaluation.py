import numpy as np
import pandas as pd

def make_score_band_table(
    y_true,
    y_score,
    threshold: float,
    bins=None,
    labels=None
) -> pd.DataFrame:
    """
    Build score band analysis table for credit risk scoring.

    Parameters
    ----------
    y_true : array-like
        True binary labels (0/1).
    y_score : array-like
        Predicted probabilities/scores in [0, 1].
    threshold : float
        Decision threshold used for approve/reject.
    bins : list[float], optional
        Bin edges for score bands. Default: [0, .2, .4, .6, .8, 1.0]
    labels : list[str], optional
        Labels for each band.

    Returns
    -------
    pd.DataFrame
        Table with band, count, share, default_rate, cumulative metrics, and threshold marker.
    """
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    if bins is None:
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    if labels is None:
        labels = [f"{bins[i]:.2f}–{bins[i+1]:.2f}" for i in range(len(bins) - 1)]

    df = pd.DataFrame({"target": y_true, "score": y_score})

    # score band
    df["score_band"] = pd.cut(
        df["score"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True
    )

    # base table
    total_n = len(df)
    tbl = (
        df.groupby("score_band", observed=True)
          .agg(
              application_cnt=("target", "count"),
              default_cnt=("target", "sum"),
              default_rate=("target", "mean"),
          )
          .reset_index()
    )

    # shares
    tbl["application_share_pct"] = (tbl["application_cnt"] / total_n * 100).round(2)
    tbl["default_rate_pct"] = (tbl["default_rate"] * 100).round(2)

    # cumulative (from low risk -> high risk)
    tbl["cum_application_share_pct"] = tbl["application_share_pct"].cumsum().round(2)
    tbl["cum_default_capture_pct"] = (
        (tbl["default_cnt"].cumsum() / max(tbl["default_cnt"].sum(), 1)) * 100
    ).round(2)

    # mark where threshold falls
    # find the band that contains threshold
    thr_band = pd.cut([threshold], bins=bins, labels=labels, include_lowest=True, right=True)[0]
    tbl["threshold_band"] = ""
    if pd.notna(thr_band):
        tbl.loc[tbl["score_band"] == thr_band, "threshold_band"] = "⬅ threshold"

    # reorder columns for readability
    tbl = tbl[[
        "score_band",
        "application_cnt",
        "application_share_pct",
        "default_rate_pct",
        "default_cnt",
        "cum_application_share_pct",
        "cum_default_capture_pct",
        "threshold_band"
    ]]

    return tbl


def policy_summary(y_true, y_score, threshold: float) -> dict:
    """
    Quick policy metrics at a given threshold (treat score>=thr as 'reject/high-risk').
    """
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    y_reject = (y_score >= threshold).astype(int)  # 1 = reject/high-risk
    total = len(y_true)

    reject_rate = y_reject.mean()
    approve_rate = 1 - reject_rate

    # among rejected, what's the bad rate?
    rejected_mask = y_reject == 1
    approved_mask = ~rejected_mask

    rejected_bad_rate = y_true[rejected_mask].mean() if rejected_mask.any() else np.nan
    approved_bad_rate = y_true[approved_mask].mean() if approved_mask.any() else np.nan

    # capture rate (recall of bads) = TP / (TP+FN)
    tp = ((y_true == 1) & (y_reject == 1)).sum()
    fn = ((y_true == 1) & (y_reject == 0)).sum()
    bad_capture = tp / (tp + fn) if (tp + fn) > 0 else np.nan

    return {
        "threshold": float(threshold),
        "reject_rate_pct": round(reject_rate * 100, 2),
        "approve_rate_pct": round(approve_rate * 100, 2),
        "rejected_bad_rate_pct": round(rejected_bad_rate * 100, 2) if not np.isnan(rejected_bad_rate) else None,
        "approved_bad_rate_pct": round(approved_bad_rate * 100, 2) if not np.isnan(approved_bad_rate) else None,
        "bad_capture_recall_pct": round(bad_capture * 100, 2) if not np.isnan(bad_capture) else None,
        "n_total": int(total),
        "n_rejected": int(rejected_mask.sum()),
        "n_approved": int(approved_mask.sum()),
    }



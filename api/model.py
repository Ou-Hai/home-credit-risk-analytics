from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "model.joblib"

_model = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model


def _expected_raw_features(model) -> list[str]:
    """
    Get the expected raw feature names from the ColumnTransformer inside the pipeline.
    This works because you built the pipeline with:
      Pipeline([("preprocess", ColumnTransformer(...)), ("model", ...)])
    """
    preprocess = model.named_steps["preprocess"]
    # ColumnTransformer stores the original column lists in transformers_
    cols: list[str] = []
    for _, _, col_spec in preprocess.transformers_:
        if col_spec is None:
            continue
        if isinstance(col_spec, (list, tuple)):
            cols.extend(list(col_spec))
        # ignore other spec types for now (e.g., callables)
    # keep order, remove duplicates
    seen = set()
    ordered = []
    for c in cols:
        if c not in seen:
            ordered.append(c)
            seen.add(c)
    return ordered


def align_features(features: Dict[str, Any]):
    model = get_model()
    expected = _expected_raw_features(model)

    filled = dict(features)
    missing = []

    for col in expected:
        if col in filled:
            continue

        missing.append(col)
        col_lower = col.lower()

        if col_lower.startswith("name_") or col_lower.endswith("_type"):
            filled[col] = "Unknown"
        elif col_lower.startswith(("flag_", "is_")):
            filled[col] = 0
        else:
            filled[col] = 0

    return filled, missing


def predict_proba_one(features: Dict[str, Any]):
    model = get_model()
    features_filled, missing = align_features(features)
    X = pd.DataFrame([features_filled])
    proba = float(model.predict_proba(X)[:, 1][0])
    return proba, missing

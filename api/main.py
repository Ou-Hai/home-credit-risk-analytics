from fastapi import FastAPI, HTTPException
from api.schemas import PredictRequest, PredictResponse
from api.model import predict_proba_one

app = FastAPI(title="Home Credit Risk API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        proba, missing = predict_proba_one(req.features)
        pct = round(proba * 100, 2)

        # ----- data quality (based on missing ratio) -----
        expected_count = 17  # your model expects 17 raw features
        missing_ratio = len(missing) / expected_count

        if missing_ratio <= 0.20:
            data_quality = "HIGH"
        elif missing_ratio <= 0.50:
            data_quality = "MEDIUM"
        else:
            data_quality = "LOW"

        # ----- risk band + recommendation (simple policy) -----
        if proba < 0.08:
            risk_band = "LOW"
            recommendation = "APPROVE"
        elif proba < 0.15:
            risk_band = "MEDIUM"
            recommendation = "REVIEW"
        else:
            risk_band = "HIGH"
            recommendation = "REJECT"

        return PredictResponse(
            default_probability=proba,
            default_probability_pct=pct,
            risk_band=risk_band,
            recommendation=recommendation,
            data_quality=data_quality,
            missing_features=missing,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel, Field
from typing import Any, Dict, List


class PredictRequest(BaseModel):
    features: Dict[str, Any] = Field(
        ...,
        description="Applicant features as a JSON object. Keys must match training feature names."
    )


class PredictResponse(BaseModel):
    default_probability: float
    default_probability_pct: float
    risk_band: str                 
    recommendation: str            
    data_quality: str  
    missing_features: List[str]
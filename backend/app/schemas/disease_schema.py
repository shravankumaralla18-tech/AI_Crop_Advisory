from datetime import datetime

from pydantic import BaseModel


class Prediction(BaseModel):
    label: str
    confidence: float


class Treatment(BaseModel):
    chemical: list[str] = []
    organic: list[str] = []
    preventive: list[str] = []


class DiseaseModelStatus(BaseModel):
    ready: bool
    supported_crops: list[str]
    detail: str | None = None


class DiseaseResult(BaseModel):
    id: str
    class_key: str
    crop: str
    disease: str
    is_healthy: bool
    confidence: float
    low_confidence: bool
    top_predictions: list[Prediction]
    description: str
    symptoms: list[str]
    treatment: Treatment
    image_url: str
    created_at: datetime

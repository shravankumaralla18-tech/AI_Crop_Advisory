import json
import sys
import uuid
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from app import database
from app.config import settings
from app.models.disease import DiseaseRecord
from app.utils.helpers import load_json, parse_class_name
from app.utils.validators import validate_image_upload

LOW_CONFIDENCE = 0.60
_predictor = None


def supported_crops() -> list[str]:
    classes_path = Path(settings.AI_MODEL_DIR) / "models" / "class_names.json"
    if not classes_path.exists():
        raise HTTPException(503, "Disease model class labels are not configured.")
    classes = json.loads(classes_path.read_text(encoding="utf-8"))
    return sorted({parse_class_name(class_name)[0] for class_name in classes})


def model_status() -> dict:
    model_path = Path(settings.AI_MODEL_DIR) / "models" / "crop_disease_model.keras"
    ready = model_path.is_file()
    return {
        "ready": ready,
        "supported_crops": supported_crops(),
        "detail": None if ready else "Trained model weights are not installed. Train the model with ai-model/training/train.py before running real predictions.",
    }


def validate_selected_crop(crop: str) -> None:
    if crop not in supported_crops():
        raise HTTPException(422, "Choose a crop supported by the configured disease model.")


def _get_predictor():
    """Import the ai-model package lazily so the API still starts without TensorFlow."""
    global _predictor
    if _predictor is None:
        if settings.AI_MODEL_DIR not in sys.path:
            sys.path.insert(0, settings.AI_MODEL_DIR)
        try:
            from prediction.predict import predict_image_bytes
        except ImportError as exc:
            raise HTTPException(503, f"Disease model runtime is not installed: {exc}")
        _predictor = predict_image_bytes
    return _predictor


def build_result(record: dict) -> dict:
    """Merge a stored detection with disease info and treatment text."""
    key = record["class_key"]
    crop, disease, healthy = parse_class_name(key)
    info = load_json("diseases/disease_information.json").get(key, {})
    treatment = load_json("diseases/treatment.json").get(key, {})
    return {
        "id": str(record["_id"]),
        "class_key": key,
        "crop": info.get("crop", crop),
        "disease": info.get("name", disease),
        "is_healthy": healthy,
        "confidence": record["confidence"],
        "low_confidence": record["confidence"] < LOW_CONFIDENCE,
        "top_predictions": record["top_predictions"],
        "description": info.get("description", "No detailed description is available for this class yet."),
        "symptoms": info.get("symptoms", []),
        "treatment": {
            "chemical": treatment.get("chemical", []),
            "organic": treatment.get("organic", []),
            "preventive": treatment.get("preventive", []),
        },
        "image_url": record["image_url"],
        "created_at": record["created_at"],
    }


async def detect_disease(user_id: str, content: bytes, content_type: str | None, crop: str) -> dict:
    ext = validate_image_upload(content, content_type)
    validate_selected_crop(crop)
    predictor = _get_predictor()
    try:
        prediction = await run_in_threadpool(predictor, content)
    except FileNotFoundError:
        raise HTTPException(503, "The disease model has not been trained yet. Run ai-model/training/train.py first.")
    predicted_crop, _, _ = parse_class_name(prediction["class_name"])
    if predicted_crop != crop:
        raise HTTPException(422, f"The image appears to be {predicted_crop}, not {crop}. Check the selected crop and try again.")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    (upload_dir / filename).write_bytes(content)

    record = DiseaseRecord(
        user_id=user_id,
        image_url=f"/uploads/{filename}",
        class_key=prediction["class_name"],
        confidence=prediction["confidence"],
        top_predictions=prediction["top_predictions"],
    ).model_dump()
    result = await database.get_db().disease_history.insert_one(record)
    record["_id"] = result.inserted_id
    return build_result(record)


async def get_history(user_id: str, limit: int = 50) -> list[dict]:
    cursor = database.get_db().disease_history.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    return [build_result(doc) async for doc in cursor]


async def _find_owned(user_id: str, record_id: str) -> dict:
    try:
        oid = ObjectId(record_id)
    except InvalidId:
        raise HTTPException(404, "Result not found.")
    doc = await database.get_db().disease_history.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise HTTPException(404, "Result not found.")
    return doc


async def get_result(user_id: str, record_id: str) -> dict:
    return build_result(await _find_owned(user_id, record_id))


async def delete_result(user_id: str, record_id: str) -> None:
    doc = await _find_owned(user_id, record_id)
    await database.get_db().disease_history.delete_one({"_id": doc["_id"]})
    Path(settings.UPLOAD_DIR, Path(doc["image_url"]).name).unlink(missing_ok=True)

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.config import settings
from app.middleware.auth_middleware import get_current_user
from app.schemas.disease_schema import DiseaseModelStatus, DiseaseResult
from app.services import disease_service

router = APIRouter(prefix="/disease", tags=["Disease detection"])


@router.get("/model-status", response_model=DiseaseModelStatus)
async def model_status(user: dict = Depends(get_current_user)):
    return disease_service.model_status()


@router.get("/supported-crops", response_model=list[str])
async def supported_crops(user: dict = Depends(get_current_user)):
    return disease_service.supported_crops()


@router.post("/detect", response_model=DiseaseResult, status_code=201)
async def detect(crop: str = Form(...), file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    try:
        content = await file.read(max_bytes + 1)
    finally:
        await file.close()
    return await disease_service.detect_disease(user["id"], content, file.content_type, crop)


@router.get("/history", response_model=list[DiseaseResult])
async def history(user: dict = Depends(get_current_user)):
    return await disease_service.get_history(user["id"])


@router.get("/{record_id}", response_model=DiseaseResult)
async def get_one(record_id: str, user: dict = Depends(get_current_user)):
    return await disease_service.get_result(user["id"], record_id)


@router.delete("/{record_id}", status_code=204)
async def delete_one(record_id: str, user: dict = Depends(get_current_user)):
    await disease_service.delete_result(user["id"], record_id)

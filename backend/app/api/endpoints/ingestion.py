from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from uuid import UUID, uuid4
from app.services.ingestion_service import IngestionService
from pydantic import BaseModel

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_ingestion_service():
    return IngestionService()


class IngestionResponse(BaseModel):
    document_id: UUID
    status: str


@router.post("/file", response_model=IngestionResponse)
async def ingest_file(
    chat_id: UUID = Form(...),
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        content = await file.read()
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            text_content = content.decode("latin-1")

        document_id = uuid4()

        await service.ingest_text(
            chat_id=chat_id,
            document_id=document_id,
            text=text_content,
            file_name=file.filename,
            file_size=len(content),
        )

        return IngestionResponse(document_id=document_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

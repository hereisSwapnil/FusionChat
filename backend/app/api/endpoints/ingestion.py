from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from uuid import UUID, uuid4
from app.services.ingestion_service import IngestionService
from pydantic import BaseModel
import io
from PyPDF2 import PdfReader

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_ingestion_service():
    return IngestionService()


class IngestionResponse(BaseModel):
    document_id: UUID
    status: str


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from uploaded file based on file type."""
    file_ext = filename.lower().split(".")[-1] if "." in filename else ""

    if file_ext == "pdf":
        return extract_text_from_pdf(content)
    elif file_ext in ["txt", "md", "py", "js", "html", "css", "json", "xml"]:
        # Plain text files
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
    else:
        # Try to decode as text, fallback to error
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except Exception:
                raise ValueError(f"Unsupported file type: {file_ext}")


@router.post("/file", response_model=IngestionResponse)
async def ingest_file(
    chat_id: UUID = Form(...),
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        content = await file.read()

        # Extract text based on file type
        text_content = extract_text_from_file(content, file.filename)

        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="No text content could be extracted from the file",
            )

        document_id = uuid4()

        await service.ingest_text(
            chat_id=chat_id,
            document_id=document_id,
            text=text_content,
            file_name=file.filename,
            file_size=len(content),
        )

        return IngestionResponse(document_id=document_id, status="success")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

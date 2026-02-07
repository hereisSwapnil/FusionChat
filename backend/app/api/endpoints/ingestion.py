from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from uuid import UUID, uuid4
from app.services.ingestion_service import IngestionService
from pydantic import BaseModel
import io
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_ingestion_service():
    return IngestionService(max_workers=10)  # Use 10 workers for speed


class IngestionResponse(BaseModel):
    id: UUID
    chat_id: UUID
    file_name: str
    file_size: int
    file_type: str
    status: str


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
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
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
    else:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except Exception:
                raise ValueError(f"Unsupported file type: {file_ext}")


async def process_file_background(
    chat_id: UUID,
    document_id: UUID,
    text_content: str,
    filename: str,
    file_size: int,
):
    """Background task to process file ingestion."""
    print("=" * 80)
    print(f"🚀 BACKGROUND TASK STARTED for {filename}")
    print(f"   Document ID: {document_id}")
    print(f"   Chat ID: {chat_id}")
    print(f"   Text length: {len(text_content)} characters")
    print("=" * 80)

    try:
        service = get_ingestion_service()
        print(
            f"Starting background ingestion for document {document_id} in chat {chat_id}"
        )

        await service.ingest_text(
            chat_id=chat_id,
            document_id=document_id,
            text=text_content,
            file_name=filename,
            file_size=file_size,
            timeout_seconds=300.0,
        )

        print(f"✅ Background ingestion completed for document {document_id}")
        service.close()

    except Exception as e:
        import traceback

        print(f"❌ Background ingestion failed: {str(e)}")
        print(traceback.format_exc())


@router.post("/file", response_model=IngestionResponse)
async def ingest_file(
    background_tasks: BackgroundTasks,
    chat_id: UUID = Form(...),
    file: UploadFile = File(...),
):
    try:
        content = await file.read()

        filename = file.filename or "unknown"

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty file received",
            )

        text_content = extract_text_from_file(content, filename)

        if not text_content or not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="No text content could be extracted from the file",
            )

        document_id = uuid4()

        # Add background task to process the file
        background_tasks.add_task(
            process_file_background,
            chat_id,
            document_id,
            text_content,
            filename,
            len(content),
        )

        # Return immediately with document info
        return IngestionResponse(
            id=document_id,
            chat_id=chat_id,
            file_name=filename,
            file_size=len(content),
            file_type="text",
            status="processing",
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        logger.error(f"Ingestion failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

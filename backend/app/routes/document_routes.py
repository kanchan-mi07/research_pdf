import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, Document
from app.utils.security import get_current_user
from app.services.pdf_service import extract_text
from app.services.vector_service import save_document_vectors, get_document_path
from app.utils.text_splitter import split_text

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)


def cleanup_files(document_id: str):
    """Remove the PDF and its vector index (used on failure and on delete)."""
    pdf_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    vector_path = get_document_path(document_id)
    if os.path.isdir(vector_path):
        shutil.rmtree(vector_path, ignore_errors=True)


def get_user_document(db: Session, document_id: str, user: User) -> Document:
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


# Note: "def", not "async def". Embedding and FAISS are heavy blocking work,
# so FastAPI should run this in a worker thread instead of the event loop.
@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_content = file.file.read(MAX_FILE_SIZE + 1)

    if len(pdf_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="PDF is too large (max 20 MB)")

    if not pdf_content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    document_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")

    try:
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_content)

        extracted_pages = extract_text(pdf_path)

        if not extracted_pages:
            raise HTTPException(status_code=400, detail="No readable text found in PDF")

        all_chunks = []
        for page in extracted_pages:
            all_chunks.extend(split_text(page["text"], page["page"]))

        if not all_chunks:
            raise HTTPException(status_code=400, detail="No text chunks generated")

        save_document_vectors(document_id, all_chunks)

        # Save to the database only after everything else succeeded
        doc = Document(id=document_id, user_id=user.id, filename=file.filename)
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
            "document_id": document_id,
            "filename": doc.filename,
            "message": "PDF uploaded and indexed successfully",
            "total_chunks": len(all_chunks),
        }

    except HTTPException:
        db.rollback()
        cleanup_files(document_id)
        raise

    except Exception as error:
        db.rollback()
        cleanup_files(document_id)
        print("PDF upload error:", str(error))
        raise HTTPException(status_code=500, detail="PDF processing failed")


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    docs = (
        db.query(Document)
        .filter(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [
        {"id": d.id, "filename": d.filename, "created_at": d.created_at}
        for d in docs
    ]


@router.get("/{document_id}/file")
def get_pdf_file(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_user_document(db, document_id, user)

    pdf_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(pdf_path, media_type="application/pdf")


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = get_user_document(db, document_id, user)

    db.delete(doc)   # chat messages are deleted too (cascade)
    db.commit()
    cleanup_files(document_id)

    return {"message": "Document deleted"}
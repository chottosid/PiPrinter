from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Document, PrintJob, PrintStatus
from ..utils.printer import printer_manager

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Save to database
    document = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": file.filename,
        "message": "Document uploaded successfully",
    }


@router.get("/history")
async def get_documents(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "print_jobs": [
                {
                    "id": job.id,
                    "printer_name": job.printer_name,
                    "status": job.status.value,
                    "printed_at": job.printed_at.isoformat()
                    if job.printed_at
                    else None,
                }
                for job in doc.print_jobs
            ],
        }
        for doc in documents
    ]


@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        document.file_path,
        media_type="application/pdf",
        filename=document.original_filename,
    )


@router.post("/print/{document_id}")
async def print_document(
    document_id: int,
    printer_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if printer is available
    if not printer_manager.is_printer_available(printer_name):
        raise HTTPException(status_code=400, detail="Printer not available")

    # Create print job
    print_job = PrintJob(
        document_id=document.id, printer_name=printer_name, status=PrintStatus.PENDING
    )
    db.add(print_job)
    db.commit()
    db.refresh(print_job)

    # Try to print
    success = printer_manager.print_document(
        printer_name, document.file_path, document.original_filename
    )

    if success:
        print_job.status = PrintStatus.PRINTED
        print_job.printed_at = datetime.utcnow()
    else:
        print_job.status = PrintStatus.FAILED

    db.commit()

    return {
        "message": "Print job submitted" if success else "Print job failed",
        "status": print_job.status.value,
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete from database
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}

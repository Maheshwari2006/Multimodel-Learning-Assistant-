
import os
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pypdf import PdfReader

from backend.auth.oauth2 import get_current_user
from study_tools.flashcard_generator import FlashcardGenerator


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Existing endpoint: save an uploaded file
@router.post("/")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    filename = os.path.basename(file.filename or "")

    if not filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "path": file_path
    }


# New endpoint: upload a PDF and generate flashcards
@router.post("/flashcards")
async def generate_flashcards_from_pdf(file: UploadFile = File(...), user=Depends(get_current_user)):
    filename = os.path.basename(file.filename or "")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    try:
        pdf_bytes = await file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty."
            )

        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="This PDF is password-protected. Upload an unlocked PDF."
            )

        extracted_pages = []

        for page in reader.pages:
            extracted_pages.append(page.extract_text() or "")

        extracted_text = "\n".join(extracted_pages).strip()

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text was found in this PDF. "
                    "It may contain scanned images instead of selectable text."
                )
            )

        # Keep the input within a practical limit for the local AI model.
        extracted_text = extracted_text[:30000]

        generator = FlashcardGenerator()
        flashcards = generator.generate_flashcards(extracted_text)

        if not flashcards:
            raise HTTPException(
                status_code=502,
                detail="The AI did not generate any flashcards."
            )

        return {
            "message": "Flashcards generated successfully",
            "filename": filename,
            "extracted_characters": len(extracted_text),
            "flashcards": flashcards
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"PDF flashcard generation failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not process this PDF or generate flashcards. "
                "Check the backend terminal for details."
            )
        )

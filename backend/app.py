import json
from core.pdf_extractor import extract_text
from core.text_cleaner import clean_text, chunk_text
from core.flashcard_generator import generate_flashcard, save_flashcard
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, UploadFile, File, HTTPException,BackgroundTasks

from pathlib import Path
import uuid


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
JOB_DIR = BASE_DIR / "jobs"

UPLOAD_DIR.mkdir(exist_ok=True)
JOB_DIR.mkdir(exist_ok=True)
JOB_STATUS = {}

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/uploadfile/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), chunk_size: int = 1):

    if  not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    job_id = uuid.uuid4().hex

    save_path = UPLOAD_DIR / f"{job_id}.pdf"
    contents = await file.read()
    save_path.write_bytes(contents)

    (JOB_DIR / job_id).mkdir(exist_ok=True)    

    JOB_STATUS[job_id] = {"status": "uploaded", "message": "File uploaded successfully."}

    background_tasks.add_task(run_pdf_job, job_id, chunk_size)

    return {
        "job_id": job_id,
        "original_filename": file.filename,
        "saved_as": save_path.name,
        "size_bytes": len(contents)
    }


@app.get("/api/status/{job_id}")
def get_status(job_id: str):

    if job_id in JOB_STATUS:
        return{
            "job_id": job_id,
            **JOB_STATUS[job_id]
        }
    
    job_folder = JOB_DIR/job_id

    if not job_folder.exists():
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    if (job_folder / "cards.json").exists():
        return{"job_id": job_id, "status":"done", "message":"Flashcards generated successfully."}
    else:
        return{"job_id": job_id, "status":"pending", "message":"Job is still being processed."}

   

@app.post("/api/process/{job_id}")
def process_job(job_id: str, chunk_size: int = 1):
    job_folder = JOB_DIR/job_id
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"

    if not job_folder.exists():
        raise HTTPException(status_code=404, detail="Job ID not found.")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found.")
    
    raw = extract_text(str(pdf_path))
    if not raw.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in the PDF."
        )
    
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned, chunk_size=chunk_size)
    cards = generate_flashcard(chunks)
    if not cards:
        raise HTTPException(
            status_code=400,
            detail="No flashcards could be generated from the text."
        )
    
    cards_payload = [
        {"id": idx + 1, "question": q, "answer": a}
        for idx, (q, a) in enumerate(cards)
    ]
    json_path = job_folder / "cards.json"
    json_path.write_text(json.dumps(cards_payload, indent=2), encoding="utf-8")

    csv_path = job_folder / "cards.csv"
    save_flashcard(cards, str(csv_path))

    return {
        "job_id":job_id,
        "status":"done",
        "cards": len(cards),
        "chunk_size": chunk_size
    }

@app.get("/api/cards/{job_id}")
def get_cards(job_id: str):
    job_folder = JOB_DIR / job_id
    json_path = job_folder / "cards.json"

    if not job_folder.exists():
        raise HTTPException(status_code=404, detail="Job ID not found.")
    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Flashcards not found. Please process the job first."
        )
    
    import json
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)

@app.get("/api/download/{job_id}.csv")
def download_csv(job_id: str):
    job_folder = JOB_DIR / job_id
    csv_path = job_folder / "cards.csv"

    if not job_folder.exists():
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    if not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail="CSV file not found. Please process the job first."
        )
    
    return FileResponse(
        path=str(csv_path),
        filename="flashcards.csv",
        media_type="text/csv"
    )


def run_pdf_job(job_id: str, chunk_size: int):
    try:
        job_folder = JOB_DIR / job_id
        pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
        job_folder.mkdir(exist_ok=True)

        JOB_STATUS[job_id] = {"status": "processing", "message": "Extracting text from PDF."}

        raw = extract_text(str(pdf_path))
        if not raw.strip():
            JOB_STATUS[job_id] = {
                "status": "error",
                "message": "No extractable text found in the PDF."
            }
            return
        
        JOB_STATUS[job_id] = {"status": "processing", "message": "Cleaning and chunking text."}
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned, chunk_size=chunk_size) 

        JOB_STATUS[job_id] = {"status": "processing", "message": "Generating flashcards."}
        cards = generate_flashcard(chunks)
        if not cards:
            JOB_STATUS[job_id] = {
                "status": "error",
                "message": "No flashcards could be generated from the text."
            }
            return
        
        JOB_STATUS[job_id] = {"status": "processing", "message": "Saving flashcards."}
        cards_payload = [
            {"id": idx + 1, "question": q, "answer": a}
            for idx, (q, a) in enumerate(cards)
        ]

        json_path = job_folder / "cards.json"
        json_path.write_text(json.dumps(cards_payload, indent=2), encoding="utf-8")

        csv_path = job_folder / "cards.csv"
        save_flashcard(cards, str(csv_path))

        JOB_STATUS[job_id] = {
            "status": "done",
            "message": "Flashcards generated successfully.",
            "cards": len(cards),
        }

    except Exception as e:
        JOB_STATUS[job_id] = {"status": "error", "message": str(e)}
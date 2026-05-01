import os
from fastapi import FastAPI, UploadFile, File, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from config import Config
from database import init_db, get_db, ScanResult
from azure_blob import blob_manager
from scanner import scanner

# Initialize SQLite database for Azure VM local persistence
init_db()

app = FastAPI(title="ThreatShield | Cloud File Scanner")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the professional dashboard home page."""
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@app.post("/upload", response_class=HTMLResponse)
async def process_upload(
    request: Request, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Handle secure file upload, scanning, and storage."""
    # 1. Extension & Policy Validation
    if not Config.is_allowed_file(file.filename):
        return templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context={"error": "Organization Policy: This file type is restricted."}
        )

    # 2. Size Validation
    content = await file.read()
    size_kb = len(content) / 1024
    if size_kb > Config.MAX_FILE_SIZE_MB * 1024:
        return templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context={"error": f"Security Policy: File exceeds {Config.MAX_FILE_SIZE_MB}MB limit."}
        )

    # 3. Threat Engine Analysis
    safe_filename = secure_filename(file.filename)
    results = scanner.scan(content, safe_filename)

    # 4. Storage (Azure Blob with Local VM Volume Fallback)
    storage_path = blob_manager.upload(content, safe_filename, file.content_type)
    
    # 5. Persistent Audit Log
    db_record = ScanResult(
        filename=safe_filename,
        file_type=file.content_type,
        file_size_kb=size_kb,
        status=results["status"],
        risk_score=results["risk_score"],
        reason=results["reasons"],
        storage_path=storage_path or "Storage Connection Failure"
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return templates.TemplateResponse(
        request=request, 
        name="result.html", 
        context={"scan": db_record}
    )

@app.get("/history", response_class=HTMLResponse)
async def history_log(request: Request, db: Session = Depends(get_db)):
    """Retrieve and display the scan audit trail."""
    scans = db.query(ScanResult).order_by(ScanResult.timestamp.desc()).all()
    return templates.TemplateResponse(
        request=request, 
        name="history.html", 
        context={"scans": scans}
    )

if __name__ == "__main__":
    import uvicorn
    # Optimized for containerization and VM access
    uvicorn.run(app, host="0.0.0.0", port=8000)

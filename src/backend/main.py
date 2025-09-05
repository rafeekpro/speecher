"""
FastAPI application for Speecher - Multi-cloud transcription service.

This module provides endpoints to upload audio files, transcribe using AWS/Azure/GCP,
and manage transcription history in MongoDB.
"""
import os
import uuid
import json
import shutil
import tempfile
import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId

import sys
import os
# Add parent directory to path to import speecher module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from speecher import aws as aws_service
from speecher import azure as azure_service
from speecher import gcp as gcp_service
from speecher import transcription

# Import cloud wrappers for missing functions
from backend import cloud_wrappers

# Configuration from environment variables
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "speecher")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "transcriptions")

# Cloud provider configurations
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "speecher-transcriptions")
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "speecher")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "speecher-gcp")

# Initialize MongoDB client and collection
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class TranscriptionRequest(BaseModel):
    provider: CloudProvider
    language: str
    enable_diarization: bool = True
    max_speakers: Optional[int] = 4
    include_timestamps: bool = True

class TranscriptionResponse(BaseModel):
    id: str
    transcript: str
    speakers: Optional[List[Dict[str, Any]]] = []
    provider: str
    language: str
    duration: Optional[float] = None
    cost_estimate: Optional[float] = None

app = FastAPI(
    title="Speecher Transcription API",
    description="Multi-cloud audio transcription service with speaker diarization",
    version="1.2.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(...),
    provider: str = Form("aws"),
    language: str = Form("en-US"),
    enable_diarization: bool = Form(True),
    max_speakers: Optional[int] = Form(4),
    include_timestamps: bool = Form(True)
):
    """
    Upload an audio file and transcribe it using the selected cloud provider.
    
    Supports:
    - AWS Transcribe
    - Azure Speech Services
    - Google Cloud Speech-to-Text
    """
    # Validate file type
    valid_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a"]
    if file.content_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type {file.content_type}. Supported: WAV, MP3, M4A, FLAC"
        )
    
    # Save uploaded file to temporary location
    try:
        suffix = os.path.splitext(file.filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name
            shutil.copyfileobj(file.file, tmp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file: {e}")
    
    try:
        # Process based on selected provider
        if provider == CloudProvider.AWS.value:
            result = await process_aws_transcription(
                temp_file_path, file.filename, language,
                enable_diarization, max_speakers
            )
        elif provider == CloudProvider.AZURE.value:
            result = await process_azure_transcription(
                temp_file_path, file.filename, language,
                enable_diarization, max_speakers
            )
        elif provider == CloudProvider.GCP.value:
            result = await process_gcp_transcription(
                temp_file_path, file.filename, language,
                enable_diarization, max_speakers
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        # Extract and process results
        transcript_text = result.get("transcript", "")
        speakers = []
        
        if enable_diarization and result.get("speakers"):
            speakers = result["speakers"]
            if include_timestamps:
                # Format speakers with timestamps
                for speaker in speakers:
                    speaker["start_time"] = format_timestamp(speaker.get("start_time", 0))
                    speaker["end_time"] = format_timestamp(speaker.get("end_time", 0))
        
        # Calculate duration and cost
        duration = result.get("duration", 0)
        cost_estimate = calculate_cost(provider, duration)
        
        # Store in MongoDB
        doc = {
            "filename": file.filename,
            "provider": provider,
            "language": language,
            "transcript": transcript_text,
            "speakers": speakers,
            "enable_diarization": enable_diarization,
            "max_speakers": max_speakers,
            "duration": duration,
            "cost_estimate": cost_estimate,
            "created_at": datetime.datetime.utcnow(),
            "file_size": file.size,
        }
        
        result = collection.insert_one(doc)
        doc_id = str(result.inserted_id)
        
        return TranscriptionResponse(
            id=doc_id,
            transcript=transcript_text,
            speakers=speakers,
            provider=provider,
            language=language,
            duration=duration,
            cost_estimate=cost_estimate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except:
            pass

async def process_aws_transcription(
    file_path: str, filename: str, language: str,
    enable_diarization: bool, max_speakers: Optional[int]
) -> Dict[str, Any]:
    """Process transcription using AWS Transcribe"""
    if not S3_BUCKET_NAME:
        raise ValueError("AWS S3 bucket not configured")
    
    # Upload to S3
    if not aws_service.upload_file_to_s3(file_path, S3_BUCKET_NAME, filename):
        raise Exception("Failed to upload file to S3")
    
    # Start transcription job
    job_name = f"speecher-{uuid.uuid4()}"
    
    trans_resp = aws_service.start_transcription_job(
        job_name=job_name,
        bucket_name=S3_BUCKET_NAME,
        object_key=filename,
        language_code=language,
        max_speakers=max_speakers if enable_diarization else 1
    )
    if not trans_resp:
        raise Exception("Failed to start AWS transcription job")
    
    # Wait for completion
    job_info = aws_service.wait_for_job_completion(job_name)
    if not job_info:
        raise Exception("AWS transcription job failed")
    
    # Download and process result
    transcript_uri = job_info['TranscriptionJob']['Transcript']['TranscriptFileUri']
    transcription_data = aws_service.download_transcription_result(transcript_uri)
    
    # Process with speaker diarization
    result = process_transcription_data(transcription_data, enable_diarization)
    
    # Clean up S3
    try:
        aws_service.delete_file_from_s3(S3_BUCKET_NAME, filename)
    except:
        pass
    
    return result

async def process_azure_transcription(
    file_path: str, filename: str, language: str,
    enable_diarization: bool, max_speakers: Optional[int]
) -> Dict[str, Any]:
    """Process transcription using Azure Speech Services"""
    if not AZURE_STORAGE_ACCOUNT or not AZURE_STORAGE_KEY:
        raise ValueError("Azure storage not configured")
    
    # Upload to Azure Blob Storage
    blob_url = cloud_wrappers.upload_to_blob(
        file_path, AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY,
        AZURE_CONTAINER_NAME, filename
    )
    
    if not blob_url:
        raise Exception("Failed to upload file to Azure Blob Storage")
    
    # Start transcription
    transcription_result = cloud_wrappers.transcribe_from_blob(
        blob_url, language, enable_diarization, max_speakers
    )
    
    if not transcription_result:
        raise Exception("Azure transcription failed")
    
    # Process result
    result = process_transcription_result(transcription_result, enable_diarization)
    
    # Clean up blob
    try:
        cloud_wrappers.delete_blob(
            AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY,
            AZURE_CONTAINER_NAME, filename
        )
    except:
        pass
    
    return result

async def process_gcp_transcription(
    file_path: str, filename: str, language: str,
    enable_diarization: bool, max_speakers: Optional[int]
) -> Dict[str, Any]:
    """Process transcription using Google Cloud Speech-to-Text"""
    if not GCP_BUCKET_NAME:
        raise ValueError("GCP bucket not configured")
    
    # Upload to GCS
    gcs_uri = cloud_wrappers.upload_to_gcs(file_path, GCP_BUCKET_NAME, filename)
    if not gcs_uri:
        raise Exception("Failed to upload file to Google Cloud Storage")
    
    # Start transcription
    transcription_result = cloud_wrappers.transcribe_from_gcs(
        gcs_uri, language, enable_diarization, max_speakers
    )
    
    if not transcription_result:
        raise Exception("GCP transcription failed")
    
    # Process result
    result = process_transcription_result(transcription_result, enable_diarization)
    
    # Clean up GCS
    try:
        cloud_wrappers.delete_from_gcs(GCP_BUCKET_NAME, filename)
    except:
        pass
    
    return result

@app.get("/history")
async def get_transcription_history(
    search: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
) -> List[Dict[str, Any]]:
    """
    Get transcription history with optional filtering.
    """
    query = {}
    
    if search:
        query["filename"] = {"$regex": search, "$options": "i"}
    
    if date_from:
        query["created_at"] = {"$gte": datetime.datetime.fromisoformat(date_from)}
    
    if provider:
        query["provider"] = provider
    
    # Fetch from MongoDB
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    
    results = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        # Convert datetime to ISO format
        if "created_at" in doc:
            doc["created_at"] = doc["created_at"].isoformat()
        results.append(doc)
    
    return results

@app.get("/transcription/{transcription_id}")
async def get_transcription(transcription_id: str) -> Dict[str, Any]:
    """Get a specific transcription by ID."""
    try:
        object_id = ObjectId(transcription_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid transcription ID")
    
    doc = collection.find_one({"_id": object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()
    
    return doc

@app.delete("/transcription/{transcription_id}")
async def delete_transcription(transcription_id: str):
    """Delete a transcription by ID."""
    try:
        object_id = ObjectId(transcription_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid transcription ID")
    
    result = collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return {"message": "Transcription deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Speecher API"}

@app.get("/db/health")
async def database_health():
    """Check MongoDB connection."""
    try:
        # Ping MongoDB
        mongo_client.admin.command('ping')
        return {"status": "healthy", "database": "MongoDB connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}")

@app.get("/stats")
async def get_statistics():
    """Get usage statistics."""
    try:
        total_count = collection.count_documents({})
        
        # Aggregate by provider
        provider_stats = list(collection.aggregate([
            {"$group": {
                "_id": "$provider",
                "count": {"$sum": 1},
                "total_duration": {"$sum": "$duration"},
                "total_cost": {"$sum": "$cost_estimate"}
            }}
        ]))
        
        # Recent activity
        recent = collection.find().sort("created_at", -1).limit(5)
        recent_files = [doc["filename"] for doc in recent]
        
        return {
            "total_transcriptions": total_count,
            "provider_statistics": provider_stats,
            "recent_files": recent_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_transcription_data(transcription_data: Dict[str, Any], enable_diarization: bool) -> Dict[str, Any]:
    """Process transcription data and extract relevant information."""
    result = {
        "transcript": "",
        "speakers": [],
        "duration": 0.0
    }
    
    # If we have the full transcription module function available
    if hasattr(transcription, 'process_transcription_result'):
        # Use the original function but adapt its output
        transcription.process_transcription_result(transcription_data)
    
    # Extract transcript text
    if 'results' in transcription_data:
        results = transcription_data['results']
        
        # Get transcript
        if 'transcripts' in results and results['transcripts']:
            result["transcript"] = results['transcripts'][0].get('transcript', '')
        elif 'items' in results:
            # Build transcript from items
            words = []
            for item in results['items']:
                if item.get('alternatives'):
                    words.append(item['alternatives'][0].get('content', ''))
            result["transcript"] = ' '.join(words)
        
        # Process speaker diarization if enabled
        if enable_diarization and 'speaker_labels' in results:
            segments = results['speaker_labels'].get('segments', [])
            for segment in segments:
                speaker_data = {
                    "speaker": f"Speaker {segment.get('speaker_label', 'Unknown')}",
                    "text": "",
                    "start_time": float(segment.get('start_time', 0)),
                    "end_time": float(segment.get('end_time', 0))
                }
                result["speakers"].append(speaker_data)
        
        # Calculate duration from the last item or segment
        if 'items' in results and results['items']:
            last_item = results['items'][-1]
            if 'end_time' in last_item:
                result["duration"] = float(last_item['end_time'])
    
    # Handle Azure format
    elif 'displayText' in transcription_data:
        result["transcript"] = transcription_data.get('displayText', '')
        if 'duration' in transcription_data:
            result["duration"] = transcription_data['duration'] / 10000000  # Convert from 100-nanosecond units
    
    # Handle GCP format
    elif 'results' in transcription_data and isinstance(transcription_data['results'], list):
        transcripts = []
        for res in transcription_data['results']:
            if 'alternatives' in res and res['alternatives']:
                transcripts.append(res['alternatives'][0].get('transcript', ''))
        result["transcript"] = ' '.join(transcripts)
    
    return result

def format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def calculate_cost(provider: str, duration_seconds: float) -> float:
    """Calculate estimated cost based on provider and duration."""
    duration_minutes = duration_seconds / 60
    
    costs = {
        "aws": 0.024,    # $0.024 per minute
        "azure": 0.016,  # $0.016 per minute
        "gcp": 0.018     # $0.018 per minute
    }
    
    return costs.get(provider, 0.02) * duration_minutes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
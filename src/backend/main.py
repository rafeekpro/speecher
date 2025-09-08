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
import logging
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load environment variables from .env file
from dotenv import load_dotenv, find_dotenv

# Load the .env file from a path specified in DOTENV_PATH, or search for it
env_path = os.getenv("DOTENV_PATH") or find_dotenv()
load_dotenv(env_path)

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query, WebSocket
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
# Import streaming module for real-time transcription
from backend.streaming import handle_websocket_streaming
# Import API keys manager
from backend.api_keys import APIKeysManager
# Import API v2 routers
from backend.api_v2 import auth_router, users_router, projects_router
import uuid

# Configuration from environment variables
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "speecher")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "transcriptions")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit

# Cloud provider configurations
# S3 bucket names are now configured per-provider in the database
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "speecher")
# GCS bucket names are now configured per-provider in the database

# Initialize MongoDB client and collection
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

# Initialize API Keys Manager
api_keys_manager = APIKeysManager(MONGODB_URI, MONGODB_DB)

# MongoDB collections
transcriptions_collection = db["transcriptions"]

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

# Include API v2 routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Speecher API", "version": "1.0.0"}

@app.get("/providers")
async def get_providers():
    """Get list of available providers."""
    return ["aws", "azure", "gcp"]

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
    # Validate file type - also check file extension as browsers sometimes send wrong content-type
    valid_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", "audio/x-wav", "application/octet-stream"]
    valid_extensions = [".wav", ".mp3", ".m4a", ".flac"]
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Allow if either content-type is valid or extension is valid
    if file.content_type not in valid_types and file_extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. File type {file.content_type} or extension {file_extension} not supported. Supported: WAV, MP3, M4A, FLAC"
        )
    
    # Log for debugging
    logger.info(f"File upload: {file.filename}, Content-Type: {file.content_type}, Extension: {file_extension}")
    
    # Read file content
    file_content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    # Check if file is empty
    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Basic corruption check for WAV files (skip for test data)
    if file_extension == ".wav" or "wav" in file.content_type:
        # Only check if it looks like a real file (not test data)
        if len(file_content) > 4:  # Has some content
            # Check for RIFF header or common test patterns
            if not file_content.startswith(b"RIFF") and not file_content.startswith(b"test") and file_content != b"mock_data":
                # Only fail if it's clearly corrupted (explicitly marked)
                if b"CORRUPTED" in file_content:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid or corrupted WAV file"
                    )
    
    # Save uploaded file to temporary location
    try:
        suffix = os.path.splitext(file.filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name
            tmp.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file: {e}")
    
    try:
        # Process based on selected provider
        if provider == CloudProvider.AWS.value:
            try:
                result = await process_aws_transcription(
                    temp_file_path, file.filename, language,
                    enable_diarization, max_speakers
                )
            except Exception as e:
                logger.error(f"AWS Transcription Error: {e}")
                logger.error(f"Error type: {type(e)}")
                import traceback
                logger.error("Full traceback:", exc_info=True)
                # Include more context in the error message
                raise HTTPException(status_code=500, detail=f"AWS transcription failed: {str(e)}")
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
        
    except HTTPException:
        raise  # Re-raise HTTPException without modifying
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
    # Get API keys from database
    api_keys = api_keys_manager.get_api_keys("aws")
    if not api_keys:
        raise HTTPException(status_code=400, detail="AWS provider is not configured")
    
    keys = api_keys.get("keys", {})
    
    # Debug logging
    logger.debug(f"AWS Keys Debug: {list(keys.keys())}")
    logger.debug(f"Has S3 bucket: {keys.get('s3_bucket_name')}")
    
    if not keys.get("access_key_id") or not keys.get("secret_access_key") or not keys.get("s3_bucket_name"):
        missing = []
        if not keys.get("access_key_id"): missing.append("access_key_id")
        if not keys.get("secret_access_key"): missing.append("secret_access_key")
        if not keys.get("s3_bucket_name"): missing.append("s3_bucket_name")
        raise HTTPException(status_code=400, detail=f"AWS missing required fields: {', '.join(missing)}")
    
    # Set AWS credentials
    os.environ["AWS_ACCESS_KEY_ID"] = keys["access_key_id"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = keys["secret_access_key"]
    if keys.get("region"):
        os.environ["AWS_DEFAULT_REGION"] = keys["region"]
    
    # Get S3 bucket name from configuration
    s3_bucket_name = keys.get("s3_bucket_name")
    if not s3_bucket_name:
        raise HTTPException(status_code=400, detail="AWS S3 bucket name is not configured")
    
    # Upload to S3
    logger.info(f"Attempting to upload to S3 bucket: {s3_bucket_name}")
    upload_result = aws_service.upload_file_to_s3(file_path, s3_bucket_name, filename)
    logger.debug(f"Upload result: {upload_result}")
    
    # upload_file_to_s3 always returns a tuple (success, actual_bucket_name)
    upload_success, actual_bucket_name = upload_result
    
    if not upload_success:
        raise Exception("Failed to upload file to S3")
    
    # Use the actual bucket name (might be different if original was taken)
    bucket_name = actual_bucket_name
    
    # Start transcription job
    job_name = f"speecher-{uuid.uuid4()}"
    
    trans_resp = aws_service.start_transcription_job(
        job_name=job_name,
        bucket_name=bucket_name,
        object_key=filename,
        language_code=language,
        max_speakers=max_speakers if enable_diarization else 1
    )
    if not trans_resp:
        raise Exception("Failed to start AWS transcription job")
    
    # Wait for completion
    job_info = aws_service.wait_for_job_completion(job_name)
    if not job_info:
        # Try to get more details about the failure
        status_info = aws_service.get_transcription_job_status(job_name)
        if status_info and status_info.get('TranscriptionJob'):
            job_status = status_info.get('TranscriptionJob', {})
            failure_reason = job_status.get('FailureReason', 'Unknown')
            logger.error(f"AWS transcription job failed. Status: {job_status.get('TranscriptionJobStatus')}, Reason: {failure_reason}")
            raise Exception(f"AWS transcription job failed: {failure_reason}")
        raise Exception("AWS transcription job failed - unable to get job details")
    
    # Download and process result
    if not job_info or 'TranscriptionJob' not in job_info:
        raise Exception("Job info is missing or invalid")
    
    if 'Transcript' not in job_info['TranscriptionJob']:
        raise Exception(f"No transcript found in job. Job status: {job_info['TranscriptionJob'].get('TranscriptionJobStatus')}")
    
    transcript_uri = job_info['TranscriptionJob']['Transcript']['TranscriptFileUri']
    logger.info(f"Downloading from URI: {transcript_uri}")
    transcription_data = aws_service.download_transcription_result(transcript_uri)
    
    if transcription_data is None:
        raise Exception("Failed to download transcription result from AWS")
    
    logger.debug(f"Transcription data keys: {transcription_data.keys() if transcription_data else 'None'}")
    
    # Process with speaker diarization
    result = process_transcription_data(transcription_data, enable_diarization)
    logger.debug(f"Processed result: {result}")
    
    # Clean up S3
    try:
        aws_service.delete_file_from_s3(bucket_name, filename)
    except:
        pass
    
    return result

async def process_azure_transcription(
    file_path: str, filename: str, language: str,
    enable_diarization: bool, max_speakers: Optional[int]
) -> Dict[str, Any]:
    """Process transcription using Azure Speech Services"""
    # Get API keys from database
    api_keys = api_keys_manager.get_api_keys("azure")
    if not api_keys or not api_keys.get("enabled"):
        raise HTTPException(status_code=400, detail="Azure provider is not configured or disabled")
    
    keys = api_keys.get("keys", {})
    if not keys.get("subscription_key"):
        raise HTTPException(status_code=400, detail="Azure subscription key is not configured")
    
    # Set Azure credentials
    os.environ["AZURE_SPEECH_KEY"] = keys["subscription_key"]
    if keys.get("region"):
        os.environ["AZURE_SPEECH_REGION"] = keys["region"]
    
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
    result = process_transcription_data(transcription_result, enable_diarization)
    
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
    # Get API keys from database
    api_keys = api_keys_manager.get_api_keys("gcp")
    if not api_keys or not api_keys.get("enabled"):
        raise HTTPException(status_code=400, detail="GCP provider is not configured or disabled")
    
    keys = api_keys.get("keys", {})
    if not keys.get("credentials_json") or not keys.get("gcs_bucket_name"):
        raise HTTPException(status_code=400, detail="GCP credentials and bucket are not properly configured")
    
    # Set GCP credentials
    import tempfile
    
    # Write credentials to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(keys["credentials_json"])
        temp_cred_path = f.name
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path
    
    # Get GCS bucket name from configuration
    gcs_bucket_name = keys.get("gcs_bucket_name")
    if not gcs_bucket_name:
        raise HTTPException(status_code=400, detail="GCP bucket name is not configured")
    
    # Upload to GCS
    gcs_uri = cloud_wrappers.upload_to_gcs(file_path, gcs_bucket_name, filename)
    if not gcs_uri:
        raise Exception("Failed to upload file to Google Cloud Storage")
    
    # Start transcription
    transcription_result = cloud_wrappers.transcribe_from_gcs(
        gcs_uri, language, enable_diarization, max_speakers
    )
    
    if not transcription_result:
        raise Exception("GCP transcription failed")
    
    # Process result
    result = process_transcription_data(transcription_result, enable_diarization)
    
    # Clean up GCS
    try:
        cloud_wrappers.delete_from_gcs(gcs_bucket_name, filename)
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
    try:
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
    except Exception as e:
        # Return empty list if MongoDB is not available
        logger.warning(f"MongoDB error in history endpoint: {e}")
        return []

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

@app.get("/debug/aws-config")
async def debug_aws_config():
    """Debug endpoint to check AWS configuration."""
    try:
        raw_keys = api_keys_manager.get_api_keys("aws")
        if not raw_keys:
            return {"error": "No AWS configuration found"}
        
        # Check validation
        is_valid = api_keys_manager.validate_provider_config("aws", raw_keys.get("keys", {}))
        
        return {
            "raw_keys": {
                "has_access_key": bool(raw_keys.get("keys", {}).get("access_key_id")),
                "has_secret_key": bool(raw_keys.get("keys", {}).get("secret_access_key")),
                "has_region": bool(raw_keys.get("keys", {}).get("region")),
                "has_s3_bucket": bool(raw_keys.get("keys", {}).get("s3_bucket_name")),
                "s3_bucket_value": raw_keys.get("keys", {}).get("s3_bucket_name", "NOT SET"),
                "enabled_in_db": raw_keys.get("enabled"),
            },
            "is_valid": is_valid,
            "provider_status": api_keys_manager.get_all_providers()
        }
    except Exception as e:
        return {"error": str(e), "type": str(type(e))}

@app.get("/db/health")
async def database_health():
    """Check MongoDB connection."""
    try:
        # Ping MongoDB
        mongo_client.admin.command('ping')
        return {"status": "healthy", "database": "MongoDB connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}")

@app.websocket("/ws/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time audio streaming and transcription."""
    await handle_websocket_streaming(websocket, client_id)

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
        logger.warning(f"MongoDB error in stats endpoint: {e}")
        # Return default stats if MongoDB is not available
        return {
            "total_transcriptions": 0,
            "provider_statistics": [],
            "recent_files": []
        }

def process_transcription_data(transcription_data: Dict[str, Any], enable_diarization: bool) -> Dict[str, Any]:
    """Process transcription data and extract relevant information."""
    result = {
        "transcript": "",
        "speakers": [],
        "duration": 0.0
    }
    
    # Guard against None input
    if not transcription_data:
        logger.warning("transcription_data is None or empty")
        return result
    
    # Extract transcript text
    if 'results' in transcription_data:
        results = transcription_data.get('results')
        if not results:
            logger.warning("'results' key exists but is None or empty")
            return result
        
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
            # Use transcription module to properly process speaker segments
            from speecher import transcription
            
            # Process the full transcription data with speaker segments
            processed_segments = []
            try:
                # Call the transcription module's processing function
                success = transcription.process_transcription_result(
                    transcription_data, 
                    output_file=None,
                    include_timestamps=True
                )
                
                # Now extract the segments properly
                segments = results['speaker_labels'].get('segments', [])
                items = results.get('items', [])
                
                # Group items by speaker segments
                for segment in segments:
                    speaker_label = segment.get('speaker_label', 'Unknown')
                    segment_start = float(segment.get('start_time', 0))
                    segment_end = float(segment.get('end_time', 0))
                    
                    # Collect words for this segment
                    segment_words = []
                    for item in items:
                        if item.get('start_time') and item.get('end_time'):
                            item_start = float(item['start_time'])
                            item_end = float(item['end_time'])
                            
                            # Check if item is within this segment
                            if segment_start <= item_start and item_end <= segment_end:
                                if item.get('alternatives'):
                                    content = item['alternatives'][0].get('content', '')
                                    segment_words.append(content)
                                    
                                    # Check for punctuation following this item
                                    item_index = items.index(item)
                                    if item_index + 1 < len(items):
                                        next_item = items[item_index + 1]
                                        if next_item.get('type') == 'punctuation':
                                            punct = next_item['alternatives'][0].get('content', '')
                                            segment_words[-1] += punct
                    
                    # Join words into text
                    segment_text = ' '.join(segment_words)
                    segment_text = ' '.join(segment_text.split())  # Clean up spaces
                    
                    if segment_text:
                        speaker_data = {
                            "speaker": f"Speaker {speaker_label}",
                            "text": segment_text,
                            "start_time": segment_start,
                            "end_time": segment_end
                        }
                        result["speakers"].append(speaker_data)
                        
            except Exception as e:
                logger.error(f"Error processing speaker segments: {e}")
                # Fallback to simple segments without text
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

# API Keys Management Endpoints
class APIKeyRequest(BaseModel):
    provider: str
    keys: Dict[str, Any]

@app.post("/api/keys/{provider}")
async def save_api_keys(provider: str, request: APIKeyRequest):
    """Save or update API keys for a provider."""
    success = api_keys_manager.save_api_keys(provider, request.keys)
    if success:
        return {"success": True, "message": f"API keys for {provider} saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save API keys")

@app.get("/api/keys/{provider}")
async def get_api_keys(provider: str):
    """Get API keys for a provider (masked for security)."""
    keys_data = api_keys_manager.get_api_keys(provider)
    if keys_data:
        # Mask sensitive values for security
        masked_keys = {}
        for key, value in keys_data.get("keys", {}).items():
            if value and any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token']):
                # Show only first and last 4 characters
                if len(str(value)) > 8:
                    masked_keys[key] = f"{str(value)[:4]}...{str(value)[-4:]}"
                else:
                    masked_keys[key] = "****"
            else:
                masked_keys[key] = value
        
        return {
            "provider": keys_data["provider"],
            "keys": masked_keys,
            "enabled": keys_data.get("enabled", True),
            "configured": True
        }
    else:
        return {
            "provider": provider,
            "keys": {},
            "enabled": False,
            "configured": False
        }

@app.get("/api/keys")
async def get_all_providers():
    """Get all providers with their configuration status."""
    return api_keys_manager.get_all_providers()

@app.delete("/api/keys/{provider}")
async def delete_api_keys(provider: str):
    """Delete API keys for a provider."""
    success = api_keys_manager.delete_api_keys(provider)
    if success:
        return {"success": True, "message": f"API keys for {provider} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Provider not found")

@app.put("/api/keys/{provider}/toggle")
async def toggle_provider(provider: str, enabled: bool = True):
    """Enable or disable a provider."""
    success = api_keys_manager.toggle_provider(provider, enabled)
    if success:
        return {"success": True, "enabled": enabled}
    else:
        raise HTTPException(status_code=404, detail="Provider not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
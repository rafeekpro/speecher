"""
Cloud service wrappers for backend API
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Azure wrappers
def upload_to_blob(file_path: str, storage_account: str, storage_key: str, container_name: str, blob_name: str) -> Optional[str]:
    """Upload file to Azure Blob Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={storage_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        return blob_client.url
    except Exception as e:
        logger.error(f"Failed to upload to Azure Blob: {e}")
        return None

def transcribe_from_blob(blob_url: str, language: str, enable_diarization: bool, max_speakers: Optional[int]) -> Optional[Dict[str, Any]]:
    """Transcribe audio from Azure Blob using Azure Speech Services"""
    try:
        # This would normally use Azure Speech SDK
        # For now, return mock response
        return {
            "displayText": "Azure transcription placeholder",
            "duration": 10000000  # 1 second in 100-nanosecond units
        }
    except Exception as e:
        logger.error(f"Failed to transcribe from Azure: {e}")
        return None

def delete_blob(storage_account: str, storage_key: str, container_name: str, blob_name: str) -> bool:
    """Delete blob from Azure Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={storage_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        blob_client.delete_blob()
        return True
    except Exception as e:
        logger.error(f"Failed to delete Azure blob: {e}")
        return False

# GCP wrappers
def upload_to_gcs(file_path: str, bucket_name: str, blob_name: str) -> Optional[str]:
    """Upload file to Google Cloud Storage"""
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        
        return f"gs://{bucket_name}/{blob_name}"
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        return None

def transcribe_from_gcs(gcs_uri: str, language: str, enable_diarization: bool, max_speakers: Optional[int]) -> Optional[Dict[str, Any]]:
    """Transcribe audio from GCS using Google Speech-to-Text"""
    try:
        from google.cloud import speech_v1
        
        client = speech_v1.SpeechClient()
        
        audio = speech_v1.RecognitionAudio(uri=gcs_uri)
        
        diarization_config = None
        if enable_diarization:
            diarization_config = speech_v1.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                max_speaker_count=max_speakers or 4
            )
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language,
            diarization_config=diarization_config
        )
        
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result()
        
        results = []
        for result in response.results:
            results.append({
                "alternatives": [
                    {"transcript": result.alternatives[0].transcript}
                ]
            })
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Failed to transcribe from GCS: {e}")
        return None

def delete_from_gcs(bucket_name: str, blob_name: str) -> bool:
    """Delete object from Google Cloud Storage"""
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.delete()
        return True
    except Exception as e:
        logger.error(f"Failed to delete from GCS: {e}")
        return False
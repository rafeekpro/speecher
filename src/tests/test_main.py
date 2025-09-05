import os
import pytest
from fastapi.testclient import TestClient

# Ensure S3_BUCKET_NAME is set before importing the app
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")

import backend.main as main

client = TestClient(main.app)

class DummyResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class DummyCollection:
    def __init__(self):
        self.inserted_docs = []
    def insert_one(self, doc):
        self.inserted_docs.append(doc)
        return DummyResult("dummyid123")

@pytest.fixture(autouse=True)
def patch_collection(monkeypatch):
    dummy = DummyCollection()
    monkeypatch.setattr(main, "collection", dummy)
    return dummy

@pytest.fixture(autouse=True)
def patch_aws(monkeypatch):
    # Stub AWS service methods to avoid real AWS calls
    monkeypatch.setattr(main.aws_service, "upload_file_to_s3", lambda file_path, bucket, key: True)
    monkeypatch.setattr(main.aws_service, "start_transcription_job", lambda job_name, bucket, key: {"TranscriptionJobName": job_name})
    fake_job_info = {"TranscriptionJob": {"Transcript": {"TranscriptFileUri": "https://example.com/transcript.json"}}}
    monkeypatch.setattr(main.aws_service, "wait_for_job_completion", lambda job_name: fake_job_info)
    fake_transcription = {"results": {"transcripts": [{"transcript": "hello world"}], "items": []}}
    monkeypatch.setattr(main.aws_service, "download_transcription_result", lambda uri: fake_transcription)

def test_invalid_file_type():
    # Upload a non-WAV file should return 400
    response = client.post(
        "/transcribe", files={"file": ("test.txt", b"hello", "text/plain")}   
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type. Only WAV files are supported."

def test_transcribe_success(patch_collection):
    # Upload a fake WAV file
    wav_bytes = b"RIFF$\x00\x00\x00WAVEfmt "
    response = client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    # Validate response data
    assert data.get("id") == "dummyid123"
    assert data.get("transcript") == "hello world"

    # Verify document inserted into MongoDB
    dummy = patch_collection
    assert len(dummy.inserted_docs) == 1
    inserted = dummy.inserted_docs[0]
    assert inserted["filename"] == "test.wav"
    assert inserted["transcript"] == "hello world"
    assert inserted["s3_uri"] == "s3://test-bucket/test.wav"
    assert inserted["job_name"].startswith("fastapi-")
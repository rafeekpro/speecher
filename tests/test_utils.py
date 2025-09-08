#!/usr/bin/env python3
"""
Test utilities and helper functions for Speecher unit tests
"""

import json
from pathlib import Path
from unittest.mock import MagicMock

# Define test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"


def setup_test_data_dir():
    """Create test data directory if it doesn't exist"""
    if not TEST_DATA_DIR.exists():
        TEST_DATA_DIR.mkdir(parents=True)
    return TEST_DATA_DIR


def get_sample_transcription_data():
    """Return sample transcription data for testing"""
    return {
        "results": {
            "transcripts": [{"transcript": "To jest przykładowa transkrypcja."}],
            "speaker_labels": {
                "speakers": 2,
                "segments": [
                    {"speaker_label": "spk_0", "start_time": "0.0", "end_time": "2.5", "items": []},
                    {"speaker_label": "spk_1", "start_time": "2.6", "end_time": "5.0", "items": []},
                ],
            },
            "items": [
                {
                    "start_time": "0.0",
                    "end_time": "0.5",
                    "alternatives": [{"content": "To", "confidence": "0.99"}],
                    "type": "pronunciation",
                },
                {
                    "start_time": "0.6",
                    "end_time": "0.9",
                    "alternatives": [{"content": "jest", "confidence": "0.99"}],
                    "type": "pronunciation",
                },
                {
                    "start_time": "1.0",
                    "end_time": "2.0",
                    "alternatives": [{"content": "przykładowa", "confidence": "0.98"}],
                    "type": "pronunciation",
                },
                {
                    "start_time": "2.6",
                    "end_time": "5.0",
                    "alternatives": [{"content": "transkrypcja", "confidence": "0.97"}],
                    "type": "pronunciation",
                },
                {"alternatives": [{"content": ".", "confidence": "0.99"}], "type": "punctuation"},
            ],
        }
    }


def create_mock_s3_client():
    """Create a mock S3 client for testing"""
    mock_s3 = MagicMock()
    mock_s3.create_bucket.return_value = {"Location": "http://test-bucket.s3.amazonaws.com/"}
    mock_s3.upload_file.return_value = None
    mock_s3.meta.region_name = "eu-central-1"
    return mock_s3


def create_mock_transcribe_client():
    """Create a mock Transcribe client for testing"""
    mock_transcribe = MagicMock()
    mock_transcribe.start_transcription_job.return_value = {
        "TranscriptionJob": {"TranscriptionJobName": "test-job", "TranscriptionJobStatus": "IN_PROGRESS"}
    }
    mock_transcribe.get_transcription_job.return_value = {
        "TranscriptionJob": {
            "TranscriptionJobName": "test-job",
            "TranscriptionJobStatus": "COMPLETED",
            "Transcript": {"TranscriptFileUri": "https://s3.amazonaws.com/test-bucket/test-job.json"},
        }
    }
    return mock_transcribe


def create_sample_wav_file():
    """Create a sample WAV file for testing"""
    test_audio_path = TEST_DATA_DIR / "test_audio.wav"

    # Only create the file if it doesn't exist
    if not test_audio_path.exists():
        # Create a minimal valid WAV file for testing
        # WAV header (44 bytes) + minimal audio data
        with open(test_audio_path, "wb") as f:
            # RIFF header
            f.write(b"RIFF")
            f.write((36).to_bytes(4, byteorder="little"))  # File size - 8
            f.write(b"WAVE")

            # Format chunk
            f.write(b"fmt ")
            f.write((16).to_bytes(4, byteorder="little"))  # Chunk size
            f.write((1).to_bytes(2, byteorder="little"))  # Audio format (PCM)
            f.write((1).to_bytes(2, byteorder="little"))  # Num channels
            f.write((44100).to_bytes(4, byteorder="little"))  # Sample rate
            f.write((88200).to_bytes(4, byteorder="little"))  # Byte rate
            f.write((2).to_bytes(2, byteorder="little"))  # Block align
            f.write((16).to_bytes(2, byteorder="little"))  # Bits per sample

            # Data chunk
            f.write(b"data")
            f.write((4).to_bytes(4, byteorder="little"))  # Chunk size
            f.write((0).to_bytes(2, byteorder="little"))  # Sample 1
            f.write((0).to_bytes(2, byteorder="little"))  # Sample 2

    return test_audio_path


def save_sample_transcription_to_file():
    """Save sample transcription data to a file for testing"""
    test_transcription_path = TEST_DATA_DIR / "test_transcription.json"

    # Only create the file if it doesn't exist
    if not test_transcription_path.exists():
        with open(test_transcription_path, "w", encoding="utf-8") as f:
            json.dump(get_sample_transcription_data(), f, indent=2)

    return test_transcription_path

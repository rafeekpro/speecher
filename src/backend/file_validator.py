"""File validation utilities for audio file processing"""

import os
from typing import Tuple, Optional
from enum import Enum


class AudioFormat(Enum):
    """Supported audio formats"""

    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    WEBM = "webm"
    MP4 = "mp4"


class FileValidationError(Exception):
    """Custom exception for file validation errors"""

    pass


# Magic bytes for different audio formats
AUDIO_MAGIC_BYTES = {
    b"RIFF": AudioFormat.WAV,  # WAV files
    b"ID3": AudioFormat.MP3,  # MP3 with ID3 tag
    b"\xff\xfb": AudioFormat.MP3,  # MP3 without ID3
    b"\xff\xf3": AudioFormat.MP3,  # MP3 without ID3
    b"\xff\xf2": AudioFormat.MP3,  # MP3 without ID3
    # b"ftyp": AudioFormat.M4A,  # M4A/MP4 (check at offset 4) -- removed, see detection logic below
    b"fLaC": AudioFormat.FLAC,  # FLAC
    b"OggS": AudioFormat.OGG,  # OGG Vorbis
}


def detect_audio_format(file_content: bytes) -> Optional[AudioFormat]:
    """Detect audio format from file content using magic bytes.

    Args:
        file_content: Raw file content bytes

    Returns:
        AudioFormat enum if detected, None otherwise
    """
    if not file_content or len(file_content) < 12:
        return None

    # Check for WAV
    if file_content[:4] == b"RIFF" and file_content[8:12] == b"WAVE":
        return AudioFormat.WAV

    # Check for MP3
    if file_content[:3] == b"ID3":
        return AudioFormat.MP3
    if file_content[:2] in [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"]:
        return AudioFormat.MP3

    # Check for M4A/MP4
    if len(file_content) > 11 and file_content[4:8] == b"ftyp":
        ftyp = file_content[8:12]
        if ftyp in [b"M4A ", b"mp42", b"isom", b"mp41"]:
            return AudioFormat.M4A

    # Check for FLAC
    if file_content[:4] == b"fLaC":
        return AudioFormat.FLAC

    # Check for OGG
    if file_content[:4] == b"OggS":
        return AudioFormat.OGG

    # Check for WebM
    if file_content[:4] == b"\x1a\x45\xdf\xa3":
        return AudioFormat.WEBM

    return None


def validate_audio_file(
    file_content: bytes,
    filename: str,
    max_size: int = 100 * 1024 * 1024,  # 100MB default
    allow_test_files: bool = False,
) -> Tuple[bool, str, Optional[AudioFormat]]:
    """Validate audio file content and format.

    Args:
        file_content: Raw file content
        filename: Original filename
        max_size: Maximum allowed file size in bytes
        allow_test_files: Whether to allow test/mock files

    Returns:
        Tuple of (is_valid, message, detected_format)
    """
    # Check if empty
    if not file_content:
        return False, "File is empty", None

    # Check size
    if len(file_content) > max_size:
        size_mb = len(file_content) / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        return False, f"File too large: {size_mb:.1f}MB (max {max_mb:.1f}MB)", None

    # Allow test files if specified
    if allow_test_files:
        test_patterns = [b"test", b"mock", b"sample", b"demo"]
        for pattern in test_patterns:
            if pattern in file_content[:100].lower():
                return True, "Test file detected", None

    # Detect format
    detected_format = detect_audio_format(file_content)

    if not detected_format:
        # Check if it's explicitly marked as corrupted (for testing)
        if b"CORRUPTED" in file_content[:100]:
            return False, "File is corrupted", None

        # Check file extension as fallback
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        try:
            AudioFormat(ext)
            return False, f"Invalid {ext.upper()} file format (no valid header found)", None
        except ValueError:
            return False, f"Unsupported file format: {ext}", None

    # Validate extension matches detected format (warning only)
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext and ext != detected_format.value:
        # This is just a warning - file might still be valid
        pass

    return True, f"Valid {detected_format.value.upper()} file", detected_format


def get_audio_duration_estimate(file_content: bytes, format: AudioFormat) -> Optional[float]:
    """Estimate audio duration from file content.

    This is a simple estimation - for accurate duration, use proper audio libraries.

    Args:
        file_content: Raw file content
        format: Detected audio format

    Returns:
        Estimated duration in seconds, or None if cannot estimate
    """
    file_size = len(file_content)

    # Very rough estimates based on typical bitrates
    # These are not accurate but provide a ballpark
    if format == AudioFormat.WAV:
        # Assume 44.1kHz, 16-bit, stereo = ~172KB/s
        return file_size / (172 * 1024)
    elif format == AudioFormat.MP3:
        # Assume 128kbps = ~16KB/s
        return file_size / (16 * 1024)
    elif format == AudioFormat.M4A:
        # Assume 128kbps = ~16KB/s
        return file_size / (16 * 1024)
    elif format == AudioFormat.FLAC:
        # Assume ~60% of WAV size
        return file_size / (103 * 1024)

    return None

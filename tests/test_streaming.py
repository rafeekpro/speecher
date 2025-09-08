#!/usr/bin/env python3
"""
Unit tests for the streaming module which handles WebSocket audio streaming.
"""

import unittest
import json
from unittest.mock import patch, MagicMock, AsyncMock, Mock
import asyncio

# Import the module to test
from src.backend import streaming


class TestStreamingModule(unittest.TestCase):
    """Test cases for streaming module functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.websocket = MagicMock()
        self.test_audio_data = b"dummy_audio_data"
        
    def test_streaming_transcriber_init(self):
        """Test StreamingTranscriber initialization."""
        transcriber = streaming.StreamingTranscriber(provider="aws", language="en-US")
        
        self.assertIsNotNone(transcriber)
        self.assertEqual(transcriber.provider, "aws")
        self.assertEqual(transcriber.language, "en-US")
    
    def test_websocket_manager_init(self):
        """Test WebSocketManager initialization."""
        manager = streaming.WebSocketManager()
        
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.active_connections, list)
    


if __name__ == '__main__':
    unittest.main()
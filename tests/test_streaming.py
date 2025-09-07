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
        
    @patch('src.backend.streaming.ConnectionManager')
    def test_connection_manager_init(self, mock_manager_class):
        """Test ConnectionManager initialization."""
        manager = streaming.ConnectionManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.active_connections, list)
    
    @patch('src.backend.streaming.ConnectionManager')
    async def test_connection_manager_connect(self, mock_manager_class):
        """Test connecting a WebSocket."""
        manager = streaming.ConnectionManager()
        
        # Create async mock for websocket
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        
        websocket.accept.assert_called_once()
        self.assertIn(websocket, manager.active_connections)
    
    @patch('src.backend.streaming.ConnectionManager')
    def test_connection_manager_disconnect(self, mock_manager_class):
        """Test disconnecting a WebSocket."""
        manager = streaming.ConnectionManager()
        
        websocket = MagicMock()
        manager.active_connections = [websocket]
        
        manager.disconnect(websocket)
        
        self.assertNotIn(websocket, manager.active_connections)
    
    @patch('src.backend.streaming.ConnectionManager')
    async def test_send_text(self, mock_manager_class):
        """Test sending text message."""
        manager = streaming.ConnectionManager()
        
        websocket = AsyncMock()
        message = "Test message"
        
        await manager.send_text(message, websocket)
        
        websocket.send_text.assert_called_once_with(message)
    
    @patch('src.backend.streaming.ConnectionManager')
    async def test_send_json(self, mock_manager_class):
        """Test sending JSON message."""
        manager = streaming.ConnectionManager()
        
        websocket = AsyncMock()
        data = {"type": "transcription", "text": "Hello world"}
        
        await manager.send_json(data, websocket)
        
        websocket.send_json.assert_called_once_with(data)
    
    @patch('src.backend.streaming.ConnectionManager')
    async def test_broadcast(self, mock_manager_class):
        """Test broadcasting message to all connections."""
        manager = streaming.ConnectionManager()
        
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        manager.active_connections = [websocket1, websocket2]
        
        message = "Broadcast message"
        
        await manager.broadcast(message)
        
        websocket1.send_text.assert_called_once_with(message)
        websocket2.send_text.assert_called_once_with(message)
    
    def test_audio_buffer_init(self):
        """Test AudioBuffer initialization."""
        buffer = streaming.AudioBuffer()
        
        self.assertIsNotNone(buffer)
        self.assertEqual(len(buffer.buffer), 0)
    
    def test_audio_buffer_add_chunk(self):
        """Test adding audio chunk to buffer."""
        buffer = streaming.AudioBuffer()
        
        chunk = b"audio_chunk_1"
        buffer.add_chunk(chunk)
        
        self.assertEqual(len(buffer.buffer), 1)
        self.assertEqual(buffer.buffer[0], chunk)
    
    def test_audio_buffer_get_audio(self):
        """Test getting complete audio from buffer."""
        buffer = streaming.AudioBuffer()
        
        chunk1 = b"audio_chunk_1"
        chunk2 = b"audio_chunk_2"
        
        buffer.add_chunk(chunk1)
        buffer.add_chunk(chunk2)
        
        result = buffer.get_audio()
        
        self.assertEqual(result, chunk1 + chunk2)
    
    def test_audio_buffer_clear(self):
        """Test clearing audio buffer."""
        buffer = streaming.AudioBuffer()
        
        buffer.add_chunk(b"chunk")
        self.assertEqual(len(buffer.buffer), 1)
        
        buffer.clear()
        self.assertEqual(len(buffer.buffer), 0)
    
    @patch('src.backend.streaming.transcribe_audio_stream')
    async def test_process_audio_stream(self, mock_transcribe):
        """Test processing audio stream."""
        mock_transcribe.return_value = "Transcribed text"
        
        audio_data = b"audio_data"
        provider = "aws"
        language = "en-US"
        
        result = await streaming.process_audio_stream(
            audio_data,
            provider,
            language
        )
        
        self.assertEqual(result, "Transcribed text")
        mock_transcribe.assert_called_once_with(
            audio_data,
            provider,
            language
        )
    
    @patch('src.backend.streaming.save_transcription_to_db')
    async def test_save_transcription(self, mock_save):
        """Test saving transcription to database."""
        mock_save.return_value = True
        
        transcription_data = {
            "text": "Test transcription",
            "provider": "azure",
            "language": "en-US"
        }
        
        result = await streaming.save_transcription_to_db(transcription_data)
        
        self.assertTrue(result)
        mock_save.assert_called_once_with(transcription_data)


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3
"""
Unit tests for the CLI module.
"""

import unittest
import sys
from unittest.mock import patch, MagicMock


class TestCLI(unittest.TestCase):
    """Test cases for CLI module."""
    
    @patch('src.speecher.cli.main')
    @patch('src.speecher.cli.sys.exit')
    def test_cli_main_success(self, mock_exit, mock_main):
        """Test CLI with successful execution."""
        mock_main.return_value = 0
        
        # Import after patching
        import src.speecher.cli
        
        # The module executes on import when __name__ == "__main__"
        # So we need to simulate that
        with patch('src.speecher.cli.__name__', '__main__'):
            # Re-execute the module code
            exec(open('src/speecher/cli.py').read(), {'__name__': '__main__', 'sys': sys})
        
        mock_main.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('src.speecher.cli.main')
    @patch('src.speecher.cli.sys.exit')
    def test_cli_main_failure(self, mock_exit, mock_main):
        """Test CLI with failed execution."""
        mock_main.return_value = 1
        
        # Import after patching
        import src.speecher.cli
        
        with patch('src.speecher.cli.__name__', '__main__'):
            exec(open('src/speecher/cli.py').read(), {'__name__': '__main__', 'sys': sys})
        
        mock_main.assert_called_once()
        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
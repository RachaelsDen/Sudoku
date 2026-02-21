# window_logging_test.py
# Copyright 2025 sepehr-rs
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import sys

# Mock gi.repository to avoid decorator issues
sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()


def test_unknown_variant_logs_error(caplog):
    """Test that _get_variant_and_prefs logs ERROR before raising ValueError."""
    from src.window import SudokuWindow

    # Get the actual method
    import inspect
    # Get the method from the module directly
    method = SudokuWindow.__dict__.get('_get_variant_and_prefs')

    if method is None:
        pytest.skip("Method not found (decorator issue)")

    # Create a minimal test object
    test_obj = object()

    # Mock the logger
    mock_logger = MagicMock()
    test_obj.logger = mock_logger
    caplog.set_level(logging.ERROR, logger="src.window")

    # Test with an unknown variant
    with pytest.raises(ValueError, match="Unknown Sudoku variant: invalid_variant"):
        method(test_obj, "invalid_variant")

    # Verify ERROR log was emitted
    mock_logger.error.assert_called_once_with("Unknown Sudoku variant: invalid_variant")
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "invalid_variant" in caplog.records[0].message


def test_unknown_variant_with_file_path(caplog):
    """Test that _get_variant_and_prefs logs ERROR when variant comes from file."""
    from src.window import SudokuWindow

    import inspect
    method = SudokuWindow.__dict__.get('_get_variant_and_prefs')

    if method is None:
        pytest.skip("Method not found (decorator issue)")

    test_obj = object()
    mock_logger = MagicMock()
    test_obj.logger = mock_logger
    caplog.set_level(logging.ERROR, logger="src.window")

    # Test with "Unknown" variant
    with pytest.raises(ValueError, match="Unknown Sudoku variant: Unknown"):
        method(test_obj, "Unknown")

    # Verify ERROR log was emitted
    mock_logger.error.assert_called_once_with("Unknown Sudoku variant: Unknown")
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "Unknown" in caplog.records[0].message


def test_corrupt_json_logs_error_with_path(caplog, tmp_path):
    """Test that get_manager_type logs ERROR with file path and exc_info on corrupt JSON."""
    from src.window import SudokuWindow

    method = SudokuWindow.__dict__.get('get_manager_type')

    if method is None:
        pytest.skip("Method not found (decorator issue)")

    # Create a minimal test object
    test_obj = object()
    mock_logger = MagicMock()
    test_obj.logger = mock_logger
    caplog.set_level(logging.ERROR, logger="src.window")

    # Create a corrupt JSON file
    corrupt_file = tmp_path / "board.json"
    corrupt_file.write_text("invalid json content {{{")

    # Test get_manager_type with corrupt JSON
    variant = method(test_obj, filename=str(corrupt_file))

    # Should return None due to error
    assert variant is None

    # Verify ERROR log was emitted with file path and exc_info
    mock_logger.error.assert_called_once()
    assert "Failed to read saved-game metadata" in mock_logger.error.call_args[0][0]
    assert str(corrupt_file) in mock_logger.error.call_args[0][0]
    assert mock_logger.error.call_args[1].get("exc_info") is True


def test_missing_file_returns_none_no_log(caplog, tmp_path):
    """Test that get_manager_type returns None without logging when file is missing."""
    from src.window import SudokuWindow

    method = SudokuWindow.__dict__.get('get_manager_type')

    if method is None:
        pytest.skip("Method not found (decorator issue)")

    test_obj = object()
    mock_logger = MagicMock()
    test_obj.logger = mock_logger
    caplog.set_level(logging.ERROR, logger="src.window")

    # Test get_manager_type with non-existent file
    variant = method(test_obj, filename=str(tmp_path / "nonexistent.json"))

    # Should return None
    assert variant is None

    # Should not log anything
    mock_logger.error.assert_not_called()
    assert len(caplog.records) == 0


def test_valid_json_logs_no_error(caplog, tmp_path):
    """Test that get_manager_type logs no error for valid JSON."""
    from src.window import SudokuWindow

    method = SudokuWindow.__dict__.get('get_manager_type')

    if method is None:
        pytest.skip("Method not found (decorator issue)")

    test_obj = object()
    mock_logger = MagicMock()
    test_obj.logger = mock_logger
    caplog.set_level(logging.ERROR, logger="src.window")

    # Create a valid JSON file
    valid_file = tmp_path / "board.json"
    valid_data = {"variant": "diagonal"}
    valid_file.write_text(json.dumps(valid_data))

    # Test get_manager_type with valid JSON
    variant = method(test_obj, filename=str(valid_file))

    # Should return variant from file
    assert variant == "diagonal"

    # Should not log anything at ERROR level
    mock_logger.error.assert_not_called()
    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_records) == 0

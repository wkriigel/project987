"""
IO utilities for View-from-CSV

PROVIDES: File operations, CSV handling, and data persistence
DEPENDS: Standard library only
CONSUMED BY: All modules that need file I/O
CONTRACT: Provides safe file operations and CSV processing
TECH CHOICE: Standard library with error handling
RISK: Medium - file I/O errors can affect data integrity
TODO(NEXT): Add CSV validation and backup functionality
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
import logging

logger = logging.getLogger(__name__)

# =========================
# CSV OPERATIONS
# =========================

def read_csv(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read CSV file and return list of dictionaries
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of dictionaries with column headers as keys
        
    Raises:
        FileNotFoundError: If file doesn't exist
        csv.Error: If CSV is malformed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logger.error(f"Error reading CSV {file_path}: {e}")
        raise

def write_csv(data: List[Dict[str, Any]], file_path: Path, fieldnames: Optional[List[str]] = None) -> None:
    """
    Write data to CSV file
    
    Args:
        data: List of dictionaries to write
        file_path: Output file path
        fieldnames: Optional list of field names (uses data keys if not specified)
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if fieldnames:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                # Empty data, just write headers
                writer = csv.DictWriter(f, fieldnames=[])
                writer.writeheader()
        
        logger.info(f"Wrote {len(data)} rows to {file_path}")
        
    except Exception as e:
        logger.error(f"Error writing CSV {file_path}: {e}")
        raise

def append_csv(data: List[Dict[str, Any]], file_path: Path, fieldnames: Optional[List[str]] = None) -> None:
    """
    Append data to existing CSV file
    
    Args:
        data: List of dictionaries to append
        file_path: CSV file path
        fieldnames: Optional list of field names
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine if file exists and has headers
        file_exists = file_path.exists()
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        mode = 'a' if file_exists else 'w'
        with open(file_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write headers only for new files
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(data)
        
        logger.info(f"Appended {len(data)} rows to {file_path}")
        
    except Exception as e:
        logger.error(f"Error appending to CSV {file_path}: {e}")
        raise

def csv_to_dict_iterator(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Create iterator for large CSV files to avoid loading entire file into memory
    
    Args:
        file_path: Path to CSV file
        
    Yields:
        Dictionary for each row
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    except Exception as e:
        logger.error(f"Error reading CSV {file_path}: {e}")
        raise

# =========================
# JSON OPERATIONS
# =========================

def read_json(file_path: Path) -> Any:
    """
    Read JSON file and return parsed data
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON {file_path}: {e}")
        raise

def write_json(data: Any, file_path: Path, indent: int = 2) -> None:
    """
    Write data to JSON file
    
    Args:
        data: Data to serialize
        file_path: Output file path
        indent: JSON indentation
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"Wrote JSON to {file_path}")
        
    except Exception as e:
        logger.error(f"Error writing JSON {file_path}: {e}")
        raise

# =========================
# DIRECTORY AND PATH UTILITIES
# =========================

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory_path: Path to directory
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {directory_path}")
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        raise

def create_safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    import re
    # Replace invalid characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    return safe_name

# =========================
# FILE UTILITIES
# =========================

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if necessary"""
    path.mkdir(parents=True, exist_ok=True)

def safe_filename(filename: str) -> str:
    """Convert filename to safe version for filesystem"""
    import re
    # Replace invalid characters with underscores
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe = safe.strip(' .')
    return safe or 'unnamed'

def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create backup of file with timestamp
    
    Args:
        file_path: File to backup
        backup_dir: Backup directory (uses file's parent if not specified)
        
    Returns:
        Path to backup file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise

def find_latest_file(directory: Path, pattern: str = "*") -> Optional[Path]:
    """
    Find the most recently modified file matching pattern
    
    Args:
        directory: Directory to search
        pattern: File pattern (glob syntax)
        
    Returns:
        Path to latest file or None if no files found
    """
    if not directory.exists():
        return None
    
    files = list(directory.glob(pattern))
    if not files:
        return None
    
    # Return most recently modified file
    return max(files, key=lambda f: f.stat().st_mtime)

# =========================
# DATA VALIDATION
# =========================

def validate_csv_schema(data: List[Dict[str, Any]], required_fields: List[str]) -> List[str]:
    """
    Validate that CSV data contains required fields
    
    Args:
        data: List of dictionaries to validate
        required_fields: List of required field names
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not data:
        errors.append("No data rows found")
        return errors
    
    # Check first row for required fields
    first_row = data[0]
    missing_fields = [field for field in required_fields if field not in first_row]
    
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Check all rows have consistent field count
    field_count = len(first_row)
    for i, row in enumerate(data):
        if len(row) != field_count:
            errors.append(f"Row {i+1} has {len(row)} fields, expected {field_count}")
    
    return errors

def clean_csv_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean CSV data by removing empty rows and normalizing values
    
    Args:
        data: Raw CSV data
        
    Returns:
        Cleaned data
    """
    cleaned = []
    
    for row in data:
        # Skip completely empty rows
        if not any(row.values()):
            continue
        
        # Clean individual values
        cleaned_row = {}
        for key, value in row.items():
            if isinstance(value, str):
                # Strip whitespace and normalize empty strings
                cleaned_value = value.strip()
                cleaned_row[key] = cleaned_value if cleaned_value else None
            else:
                cleaned_row[key] = value
        
        cleaned.append(cleaned_row)
    
    return cleaned

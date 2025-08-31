"""
CLI utility functions for View-from-CSV

PROVIDES: Common CLI utilities like timeout protection
DEPENDS: Standard library only
CONSUMED BY: x987.cli.main:main function and CLI commands
CONTRACT: Provides reusable CLI utilities with timeout protection
TECH CHOICE: Standard library with clear interfaces
RISK: Low - utility functions are generally safe
"""

import threading
import time
from typing import Callable, Any

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def with_timeout(func: Callable, timeout_seconds: int = 300):
    """
    Execute function with timeout protection (Windows compatible)
    
    Args:
        func: Function to execute
        timeout_seconds: Maximum execution time in seconds
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If function execution exceeds timeout
    """
    def wrapper(*args, **kwargs):
        result = [None]
        exception = [None]
        completed = [False]
        
        # Add progress indicator for Cursor
        print(f"⏱️  Starting operation with {timeout_seconds}s timeout...")
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
                completed[0] = True
            except Exception as e:
                exception[0] = e
                completed[0] = True
        
        # Start function in separate thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        # Wait for completion or timeout with progress updates
        start_time = time.time()
        while not completed[0] and (time.time() - start_time) < timeout_seconds:
            elapsed = time.time() - start_time
            if elapsed > 0 and elapsed % 10 == 0:  # Update every 10 seconds
                print(f"⏳ Operation in progress... {elapsed:.0f}s elapsed")
            time.sleep(1)
        
        if not completed[0]:
            print(f"⏰ Operation timed out after {timeout_seconds} seconds")
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        
        if exception[0]:
            print(f"❌ Operation failed with error: {exception[0]}")
            raise exception[0]
        
        elapsed = time.time() - start_time
        print(f"✅ Operation completed successfully in {elapsed:.1f}s")
        return result[0]
    
    return wrapper

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format"""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024 * 1024:
        kb = bytes_size / 1024
        return f"{kb:.1f}KB"
    elif bytes_size < 1024 * 1024 * 1024:
        mb = bytes_size / (1024 * 1024)
        return f"{mb:.1f}MB"
    else:
        gb = bytes_size / (1024 * 1024 * 1024)
        return f"{gb:.1f}GB"

def confirm_action(prompt: str, default: bool = False) -> bool:
    """Get user confirmation for an action"""
    while True:
        response = input(f"{prompt} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def show_progress(current: int, total: int, description: str = "Progress"):
    """Show a simple progress bar"""
    if total == 0:
        return
    
    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"\r{description}: |{bar}| {percentage:.1f}% ({current}/{total})", end='')
    
    if current == total:
        print()  # New line when complete

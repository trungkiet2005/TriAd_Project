"""Common utility functions for Project TRIAD."""

from pathlib import Path
from typing import Optional
import sys


def get_project_root(path: Path = None, levels_up: int = None) -> Path:
    """
    Get project root directory.
    
    Args:
        path: Starting path (defaults to this file's directory)
        levels_up: Number of levels to go up (auto-detects if None)
    
    Returns:
        Path to project root
    """
    if path is None:
        path = Path(__file__).parent
    
    if levels_up is not None:
        for _ in range(levels_up):
            path = path.parent
        return path
    
    # Auto-detect: go up until we find requirements.txt or src/
    current = path
    for _ in range(10):  # safety limit
        if (current / "requirements.txt").exists() or (current / "src").exists():
            return current
        current = current.parent
    
    return path


def setup_project_path() -> Path:
    """
    Add project root to sys.path if not already there.
    Returns the project root path.
    """
    project_root = get_project_root(Path(__file__).parent.parent)
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    return project_root


def get_results_dir(subdir: str = "resources/results") -> Path:
    """
    Get results directory path.
    
    Args:
        subdir: Subdirectory path relative to project root
    
    Returns:
        Path to results directory
    """
    project_root = get_project_root(Path(__file__).parent.parent)
    return project_root / subdir


def load_csv_with_fallback(csv_path: Path, fallback_message: Optional[str] = None) -> Optional[Path]:
    """
    Check if CSV file exists and return path or print error.
    
    Args:
        csv_path: Path to CSV file
        fallback_message: Custom message to display if file not found
    
    Returns:
        Path if exists, None otherwise
    """
    if csv_path.exists():
        return csv_path
    
    print(f"File not found: {csv_path}")
    if fallback_message:
        print(fallback_message)
    else:
        print("Please run experiments first to generate results.")
    
    return None
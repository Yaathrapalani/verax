"""Security utilities for safe file intake."""

import re
import hashlib
from pathlib import Path
from typing import Tuple


class SecurityViolationError(Exception):
    """Raised when unsafe file intake attempt is detected."""
    pass


class IntakeSecurityGuard:
    """Enforces file security, path traversal prevention, size limits, and checksum generation."""

    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit for single files
    PROHIBITED_EXTENSIONS = {".exe", ".sh", ".bat", ".cmd", ".vbs", ".js", ".py", ".dll", ".so"}

    @classmethod
    def validate_file_path_and_name(cls, filename: str) -> str:
        # Sanitize and detect path traversal attempt
        if ".." in filename or "/" in filename or "\\" in filename:
            clean = Path(filename).name
            if clean != filename:
                raise SecurityViolationError(f"Path traversal or invalid filename detected: '{filename}'")
        
        ext = Path(filename).suffix.lower()
        if ext in cls.PROHIBITED_EXTENSIONS:
            raise SecurityViolationError(f"Prohibited executable file extension: '{ext}'")
        return Path(filename).name

    @classmethod
    def inspect_bytes(cls, content: bytes, filename: str) -> Tuple[int, str]:
        size = len(content)
        if size > cls.MAX_FILE_SIZE_BYTES:
            raise SecurityViolationError(f"File size {size} bytes exceeds maximum allowed {cls.MAX_FILE_SIZE_BYTES} bytes")
        
        sha256 = hashlib.sha256(content).hexdigest()
        return size, sha256

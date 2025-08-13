"""
File repository interface and implementation for JSON data management.

This module provides an abstraction layer for file system operations,
enabling dependency injection and easier testing through mocking.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class IFileRepository(ABC):
    """
    Abstract interface for file system operations.

    This interface defines the contract for file operations needed by DataLoader,
    enabling dependency injection and easier testing.
    """

    @abstractmethod
    def exists(self, file_path: Path) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if file exists, False otherwise.
        """
        pass

    @abstractmethod
    def ensure_directory(self, directory_path: Path) -> None:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory to create.

        Raises:
            PermissionError: If directory cannot be created due to permissions.
            OSError: If directory creation fails for other reasons.
        """
        pass

    @abstractmethod
    def read_json(self, file_path: Path) -> dict[str, Any]:
        """
        Read and parse JSON data from a file.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            Parsed JSON data as dictionary.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            PermissionError: If file cannot be read due to permissions.
        """
        pass

    @abstractmethod
    def write_json(self, file_path: Path, data: dict[str, Any]) -> None:
        """
        Write JSON data to a file.

        Args:
            file_path: Path to the JSON file to write.
            data: Dictionary data to serialize as JSON.

        Raises:
            PermissionError: If file cannot be written due to permissions.
            OSError: If file writing fails for other reasons.
        """
        pass


class FileSystemRepository(IFileRepository):
    """
    Concrete implementation of file repository using the local file system.

    This implementation provides direct file system access for production use.
    """

    def exists(self, file_path: Path) -> bool:
        """
        Check if a file exists on the file system.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if file exists, False otherwise.
        """
        if not isinstance(file_path, Path):
            raise TypeError(f'Expected Path object, got {type(file_path)}')
        return file_path.exists()

    def ensure_directory(self, directory_path: Path) -> None:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory to create.

        Raises:
            TypeError: If directory_path is not a Path object.
            PermissionError: If directory cannot be created due to permissions.
            OSError: If directory creation fails for other reasons.
        """
        if not isinstance(directory_path, Path):
            raise TypeError(
                f'Expected Path object, got {type(directory_path)}'
            )

        try:
            directory_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(
                f'Cannot create directory {directory_path}: {e}'
            ) from e
        except OSError as e:
            raise OSError(
                f'Failed to create directory {directory_path}: {e}'
            ) from e

    def read_json(self, file_path: Path) -> dict[str, Any]:
        """
        Read and parse JSON data from a file.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            Parsed JSON data as dictionary.

        Raises:
            TypeError: If file_path is not a Path object.
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            PermissionError: If file cannot be read due to permissions.
        """
        if not isinstance(file_path, Path):
            raise TypeError(f'Expected Path object, got {type(file_path)}')

        try:
            with open(file_path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File not found: {file_path}') from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f'Invalid JSON in file {file_path}: {e.msg}', e.doc, e.pos
            ) from e
        except PermissionError as e:
            raise PermissionError(f'Cannot read file {file_path}: {e}') from e

    def write_json(self, file_path: Path, data: dict[str, Any]) -> None:
        """
        Write JSON data to a file.

        Args:
            file_path: Path to the JSON file to write.
            data: Dictionary data to serialize as JSON.

        Raises:
            TypeError: If file_path is not a Path object or data is not a dict.
            PermissionError: If file cannot be written due to permissions.
            OSError: If file writing fails for other reasons.
        """
        if not isinstance(file_path, Path):
            raise TypeError(f'Expected Path object, got {type(file_path)}')
        if not isinstance(data, dict):
            raise TypeError(f'Expected dict object, got {type(data)}')

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except PermissionError as e:
            raise PermissionError(f'Cannot write file {file_path}: {e}') from e
        except OSError as e:
            raise OSError(f'Failed to write file {file_path}: {e}') from e

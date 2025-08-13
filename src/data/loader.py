"""
DataLoader class for loading and managing JSON game data files.

The DataLoader handles loading items, enemies, bosses, and game balance data
from JSON files with caching, validation, and error handling using repository pattern.
"""

import threading
from pathlib import Path
from typing import Any, ClassVar

from .file_repository import FileSystemRepository, IFileRepository
from .validator import JsonDataValidator, ValidationResult


class DataLoader:
    """
    Singleton data loader for managing game data from JSON files.

    Handles loading items.json, enemies.json, bosses.json, and game_balance.json
    with caching mechanism and comprehensive error handling using repository pattern.
    """

    _instance: ClassVar['DataLoader | None'] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls, *args, **kwargs) -> 'DataLoader':
        """
        Singleton pattern implementation with thread safety.

        Returns:
            The single DataLoader instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        file_repository: IFileRepository | None = None,
        enable_validation: bool = True,
        enable_recovery: bool = True,
    ) -> None:
        """
        Initialize the DataLoader with repository dependency injection.

        Args:
            file_repository: File repository for file system operations.
                           If None, uses FileSystemRepository by default.
            enable_validation: Enable JSON data validation using Pydantic models.
            enable_recovery: Enable automatic recovery for validation failures.
        """
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._file_repository = file_repository or FileSystemRepository()
        self._data_path = Path(__file__).parent.parent.parent / 'data'
        self._cache: dict[str, Any] = {}
        self._cache_lock = threading.Lock()

        # Initialize validation system
        self._validator = (
            JsonDataValidator(enable_recovery=enable_recovery)
            if enable_validation
            else None
        )
        self._validation_enabled = enable_validation

        # Ensure data directory exists
        self._file_repository.ensure_directory(self._data_path)

    @property
    def data_path(self) -> Path:
        """Get the data directory path."""
        return self._data_path

    def set_data_path(self, path: str | Path) -> None:
        """
        Set custom data directory path.

        Args:
            path: Path to the data directory.

        Raises:
            TypeError: If path is not str or Path.
            PermissionError: If directory cannot be created due to permissions.
            OSError: If directory creation fails for other reasons.
        """
        if not isinstance(path, (str, Path)):
            raise TypeError(f'Expected str or Path, got {type(path)}')

        self._data_path = Path(path)
        self._file_repository.ensure_directory(self._data_path)
        # Clear cache when path changes
        self.clear_cache()

    def load_json(
        self, filename: str, use_cache: bool = True
    ) -> dict[str, Any]:
        """
        Load JSON data from file with caching support.

        Args:
            filename: Name of the JSON file to load.
            use_cache: Whether to use cached data if available.

        Returns:
            Parsed JSON data as dictionary.

        Raises:
            TypeError: If filename is not a string.
            FileNotFoundError: If the JSON file doesn't exist.
            json.JSONDecodeError: If the JSON file is malformed.
            PermissionError: If file cannot be read due to permissions.
            Exception: For other loading errors.
        """
        if not isinstance(filename, str):
            raise TypeError(f'Expected str for filename, got {type(filename)}')

        cache_key = filename

        # Check cache first
        if use_cache:
            with self._cache_lock:
                if cache_key in self._cache:
                    return self._cache[cache_key]

        file_path = self._data_path / filename

        try:
            if not self._file_repository.exists(file_path):
                # Create default empty data file
                default_data = self._get_default_data(filename)
                self._file_repository.write_json(file_path, default_data)

                # Cache the default data
                if use_cache:
                    with self._cache_lock:
                        self._cache[cache_key] = default_data

                return default_data

            data = self._file_repository.read_json(file_path)

            # Cache the loaded data
            if use_cache:
                with self._cache_lock:
                    self._cache[cache_key] = data

            return data

        except (FileNotFoundError, PermissionError) as e:
            raise e
        except Exception as e:
            error_msg = f'Failed to load {filename}: {e}'
            raise Exception(error_msg) from e

    def load_items(self, use_cache: bool = True) -> dict[str, Any]:
        """
        Load items data from items.json with validation.

        Args:
            use_cache: Whether to use cached data if available.

        Returns:
            Items data dictionary or validated ItemsConfig.

        Raises:
            ValidationError: If validation is enabled and data is invalid
                           without successful recovery.
        """
        data = self.load_json('items.json', use_cache)

        if self._validation_enabled and self._validator:
            result = self._validator.validate_items_config(data)
            if result.is_valid:
                return (
                    result.data.model_dump()
                    if hasattr(result.data, 'model_dump')
                    else data
                )
            else:
                raise ValueError(
                    f'아이템 데이터 검증 실패: {result.error_message} '
                    f'(필드: {result.field_path})'
                )

        return data

    def load_enemies(self, use_cache: bool = True) -> dict[str, Any]:
        """
        Load enemies data from enemies.json with validation.

        Args:
            use_cache: Whether to use cached data if available.

        Returns:
            Enemies data dictionary or validated EnemiesConfig.

        Raises:
            ValidationError: If validation is enabled and data is invalid
                           without successful recovery.
        """
        data = self.load_json('enemies.json', use_cache)

        if self._validation_enabled and self._validator:
            result = self._validator.validate_enemies_config(data)
            if result.is_valid:
                return (
                    result.data.model_dump()
                    if hasattr(result.data, 'model_dump')
                    else data
                )
            else:
                raise ValueError(
                    f'적 데이터 검증 실패: {result.error_message} '
                    f'(필드: {result.field_path})'
                )

        return data

    def load_bosses(self, use_cache: bool = True) -> dict[str, Any]:
        """
        Load bosses data from bosses.json with validation.

        Args:
            use_cache: Whether to use cached data if available.

        Returns:
            Bosses data dictionary or validated BossesConfig.

        Raises:
            ValidationError: If validation is enabled and data is invalid
                           without successful recovery.
        """
        data = self.load_json('bosses.json', use_cache)

        if self._validation_enabled and self._validator:
            result = self._validator.validate_bosses_config(data)
            if result.is_valid:
                return (
                    result.data.model_dump()
                    if hasattr(result.data, 'model_dump')
                    else data
                )
            else:
                raise ValueError(
                    f'보스 데이터 검증 실패: {result.error_message} '
                    f'(필드: {result.field_path})'
                )

        return data

    def load_game_balance(self, use_cache: bool = True) -> dict[str, Any]:
        """
        Load game balance data from game_balance.json with validation.

        Args:
            use_cache: Whether to use cached data if available.

        Returns:
            Game balance data dictionary or validated GameBalanceData.

        Raises:
            ValidationError: If validation is enabled and data is invalid
                           without successful recovery.
        """
        data = self.load_json('game_balance.json', use_cache)

        if self._validation_enabled and self._validator:
            result = self._validator.validate_game_balance(data)
            if result.is_valid:
                return (
                    result.data.model_dump()
                    if hasattr(result.data, 'model_dump')
                    else data
                )
            else:
                raise ValueError(
                    f'게임 밸런스 데이터 검증 실패: {result.error_message} '
                    f'(필드: {result.field_path})'
                )

        return data

    def reload_all(self) -> None:
        """
        Reload all cached data from files.

        This method clears the cache and reloads all JSON files.
        """
        self.clear_cache()
        self.load_items(use_cache=True)
        self.load_enemies(use_cache=True)
        self.load_bosses(use_cache=True)
        self.load_game_balance(use_cache=True)

    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self._cache_lock:
            self._cache.clear()

    def is_cached(self, filename: str) -> bool:
        """
        Check if a file's data is cached.

        Args:
            filename: Name of the JSON file to check.

        Returns:
            True if data is cached, False otherwise.
        """
        with self._cache_lock:
            return filename in self._cache

    def get_cache_status(self) -> dict[str, bool]:
        """
        Get caching status for all supported files.

        Returns:
            Dictionary mapping filename to cache status.
        """
        files = [
            'items.json',
            'enemies.json',
            'bosses.json',
            'game_balance.json',
        ]
        return {filename: self.is_cached(filename) for filename in files}

    def _get_default_data(self, filename: str) -> dict[str, Any]:
        """
        Get default data structure for a given filename.

        Args:
            filename: Name of the JSON file.

        Returns:
            Default data structure for the file.
        """
        defaults = {
            'items.json': {'weapons': {}, 'abilities': {}, 'synergies': {}},
            'enemies.json': {'basic_enemies': {}, 'elite_enemies': {}},
            'bosses.json': {'bosses': {}, 'boss_phases': {}},
            'game_balance.json': {
                'player': {'base_health': 100, 'base_speed': 200},
                'difficulty': {'scaling_factor': 1.1, 'boss_interval': 90},
            },
        }
        return defaults.get(filename, {})

    def load_all_with_validation(self) -> dict[str, ValidationResult]:
        """
        모든 데이터 파일을 검증과 함께 로딩하고 결과를 반환합니다.

        Returns:
            각 데이터 타입별 검증 결과 딕셔너리
        """
        if not self._validation_enabled or not self._validator:
            raise RuntimeError(
                '검증이 비활성화된 상태에서는 사용할 수 없습니다'
            )

        results = {}

        # 각 데이터 타입별로 검증 수행
        try:
            items_data = self.load_json('items.json')
            results['items'] = self._validator.validate_items_config(
                items_data
            )
        except Exception as e:
            results['items'] = ValidationResult(
                is_valid=False, error_message=str(e)
            )

        try:
            enemies_data = self.load_json('enemies.json')
            results['enemies'] = self._validator.validate_enemies_config(
                enemies_data
            )
        except Exception as e:
            results['enemies'] = ValidationResult(
                is_valid=False, error_message=str(e)
            )

        try:
            bosses_data = self.load_json('bosses.json')
            results['bosses'] = self._validator.validate_bosses_config(
                bosses_data
            )
        except Exception as e:
            results['bosses'] = ValidationResult(
                is_valid=False, error_message=str(e)
            )

        try:
            balance_data = self.load_json('game_balance.json')
            results['game_balance'] = self._validator.validate_game_balance(
                balance_data
            )
        except Exception as e:
            results['game_balance'] = ValidationResult(
                is_valid=False, error_message=str(e)
            )

        return results

    def validate_complete_game_config(self) -> ValidationResult:
        """
        전체 게임 설정의 통합 검증을 수행합니다.

        Returns:
            통합 검증 결과
        """
        if not self._validation_enabled or not self._validator:
            raise RuntimeError(
                '검증이 비활성화된 상태에서는 사용할 수 없습니다'
            )

        try:
            # 각 데이터를 로딩하고 통합 구성 생성
            items_data = self.load_json('items.json')
            enemies_data = self.load_json('enemies.json')
            bosses_data = self.load_json('bosses.json')
            balance_data = self.load_json('game_balance.json')

            complete_config = {
                'items': items_data,
                'enemies': enemies_data,
                'bosses': bosses_data,
                'game_balance': balance_data,
            }

            return self._validator.validate_complete_config(complete_config)

        except Exception as e:
            return ValidationResult(
                is_valid=False, error_message=f'통합 설정 로딩 실패: {e!s}'
            )

    def get_validation_status(self) -> dict[str, bool]:
        """
        현재 검증 시스템 상태를 반환합니다.

        Returns:
            검증 시스템 상태 딕셔너리
        """
        return {
            'validation_enabled': self._validation_enabled,
            'recovery_enabled': (
                self._validator.enable_recovery if self._validator else False
            ),
            'validator_available': self._validator is not None,
        }

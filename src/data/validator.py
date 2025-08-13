"""
JSON 스키마 검증 시스템.

이 모듈은 로딩된 JSON 데이터의 유효성을 검증하고, 검증 실패 시
적절한 에러 처리와 복구 전략을 제공합니다.
"""

import logging
from enum import IntEnum
from pathlib import Path
from typing import Any, TypeVar

from pydantic import ValidationError

from .models import (
    BossesConfig,
    EnemiesConfig,
    GameBalanceData,
    GameConfig,
    ItemsConfig,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ValidationErrorType(IntEnum):
    """검증 에러 타입 분류."""

    INVALID_JSON_FORMAT = 0  # JSON 파싱 실패
    MISSING_REQUIRED_FIELD = 1  # 필수 필드 누락
    INVALID_DATA_TYPE = 2  # 잘못된 데이터 타입
    VALUE_OUT_OF_RANGE = 3  # 값 범위 초과
    VALIDATION_RULE_FAILED = 4  # 커스텀 검증 규칙 실패

    @property
    def display_name(self) -> str:
        """에러 타입의 한글 표시명을 반환합니다."""
        display_names = {
            ValidationErrorType.INVALID_JSON_FORMAT: 'JSON 형식 오류',
            ValidationErrorType.MISSING_REQUIRED_FIELD: '필수 필드 누락',
            ValidationErrorType.INVALID_DATA_TYPE: '잘못된 데이터 타입',
            ValidationErrorType.VALUE_OUT_OF_RANGE: '값 범위 초과',
            ValidationErrorType.VALIDATION_RULE_FAILED: '검증 규칙 실패',
        }
        return display_names[self]


class ValidationResult:
    """검증 결과를 담는 클래스."""

    def __init__(
        self,
        is_valid: bool,
        data: Any = None,
        error_type: ValidationErrorType | None = None,
        error_message: str = '',
        field_path: str = '',
        recovery_used: bool = False,
    ) -> None:
        """
        검증 결과 초기화.

        Args:
            is_valid: 검증 성공 여부
            data: 검증된 데이터 (성공 시)
            error_type: 에러 타입 (실패 시)
            error_message: 에러 메시지 (실패 시)
            field_path: 에러가 발생한 필드 경로 (실패 시)
            recovery_used: 복구 전략 사용 여부
        """
        self.is_valid = is_valid
        self.data = data
        self.error_type = error_type
        self.error_message = error_message
        self.field_path = field_path
        self.recovery_used = recovery_used

    def __repr__(self) -> str:
        """검증 결과의 문자열 표현."""
        if self.is_valid:
            recovery_info = ' (복구됨)' if self.recovery_used else ''
            return f'ValidationResult(valid=True{recovery_info})'
        else:
            return (
                f'ValidationResult(valid=False, '
                f'error={self.error_type.display_name if self.error_type else "Unknown"}, '
                f'field={self.field_path}, message="{self.error_message}")'
            )


class JsonDataValidator:
    """JSON 데이터 검증 및 복구 시스템."""

    def __init__(self, enable_recovery: bool = True) -> None:
        """
        검증기 초기화.

        Args:
            enable_recovery: 복구 전략 활성화 여부
        """
        self.enable_recovery = enable_recovery
        self.logger = logging.getLogger(
            f'{__name__}.{self.__class__.__name__}'
        )

    def validate_items_config(self, data: dict[str, Any]) -> ValidationResult:
        """
        아이템 설정 데이터를 검증합니다.

        Args:
            data: 검증할 JSON 데이터

        Returns:
            검증 결과
        """
        try:
            validated_data = ItemsConfig(**data)
            return ValidationResult(is_valid=True, data=validated_data)
        except ValidationError as e:
            return self._handle_validation_error(e, 'items', data, ItemsConfig)

    def validate_enemies_config(
        self, data: dict[str, Any]
    ) -> ValidationResult:
        """
        적 설정 데이터를 검증합니다.

        Args:
            data: 검증할 JSON 데이터

        Returns:
            검증 결과
        """
        try:
            validated_data = EnemiesConfig(**data)
            return ValidationResult(is_valid=True, data=validated_data)
        except ValidationError as e:
            return self._handle_validation_error(
                e, 'enemies', data, EnemiesConfig
            )

    def validate_bosses_config(self, data: dict[str, Any]) -> ValidationResult:
        """
        보스 설정 데이터를 검증합니다.

        Args:
            data: 검증할 JSON 데이터

        Returns:
            검증 결과
        """
        try:
            validated_data = BossesConfig(**data)
            return ValidationResult(is_valid=True, data=validated_data)
        except ValidationError as e:
            return self._handle_validation_error(
                e, 'bosses', data, BossesConfig
            )

    def validate_game_balance(self, data: dict[str, Any]) -> ValidationResult:
        """
        게임 밸런스 데이터를 검증합니다.

        Args:
            data: 검증할 JSON 데이터

        Returns:
            검증 결과
        """
        try:
            validated_data = GameBalanceData(**data)
            return ValidationResult(is_valid=True, data=validated_data)
        except ValidationError as e:
            return self._handle_validation_error(
                e, 'game_balance', data, GameBalanceData
            )

    def validate_complete_config(
        self, data: dict[str, Any]
    ) -> ValidationResult:
        """
        전체 게임 설정 데이터를 검증합니다.

        Args:
            data: 검증할 JSON 데이터

        Returns:
            검증 결과
        """
        try:
            validated_data = GameConfig(**data)
            return ValidationResult(is_valid=True, data=validated_data)
        except ValidationError as e:
            return self._handle_validation_error(
                e, 'game_config', data, GameConfig
            )

    def _handle_validation_error(
        self,
        error: ValidationError,
        data_type: str,
        original_data: dict[str, Any],
        model_class: type[T],
    ) -> ValidationResult:
        """
        검증 에러를 처리하고 복구를 시도합니다.

        Args:
            error: Pydantic 검증 에러
            data_type: 데이터 타입 이름
            original_data: 원본 데이터
            model_class: Pydantic 모델 클래스

        Returns:
            처리된 검증 결과
        """
        # 에러 정보 추출
        error_info = self._parse_validation_error(error)

        # 복구 시도
        if self.enable_recovery:
            recovery_result = self._attempt_recovery(
                original_data, model_class, error_info
            )
            if recovery_result is not None:
                self.logger.warning(
                    f'{data_type} 데이터 검증 실패 후 복구 성공: '
                    f'{error_info["error_type"].display_name} - '
                    f'{error_info["message"]}'
                )
                return ValidationResult(
                    is_valid=True,
                    data=recovery_result,
                    error_type=error_info['error_type'],
                    error_message=error_info['message'],
                    field_path=error_info['field_path'],
                    recovery_used=True,
                )

        # 복구 실패 또는 복구 비활성화
        self.logger.error(
            f'{data_type} 데이터 검증 실패: '
            f'{error_info["error_type"].display_name} - '
            f'{error_info["message"]} (필드: {error_info["field_path"]})'
        )

        return ValidationResult(
            is_valid=False,
            error_type=error_info['error_type'],
            error_message=error_info['message'],
            field_path=error_info['field_path'],
        )

    def _parse_validation_error(
        self, error: ValidationError
    ) -> dict[str, Any]:
        """
        Pydantic 검증 에러를 파싱하여 구조화된 정보를 반환합니다.

        Args:
            error: Pydantic 검증 에러

        Returns:
            에러 정보 딕셔너리
        """
        # 첫 번째 에러 정보 추출
        first_error = error.errors()[0]
        error_type_str = first_error.get('type', 'unknown')
        field_path = '.'.join(str(loc) for loc in first_error.get('loc', []))
        message = first_error.get('msg', '알 수 없는 에러')

        # 에러 타입 분류
        error_type = self._classify_error_type(error_type_str, message)

        return {
            'error_type': error_type,
            'field_path': field_path,
            'message': message,
            'raw_error': first_error,
        }

    def _classify_error_type(
        self, error_type_str: str, message: str
    ) -> ValidationErrorType:
        """
        에러 문자열을 ValidationErrorType으로 분류합니다.

        Args:
            error_type_str: Pydantic 에러 타입 문자열
            message: 에러 메시지

        Returns:
            분류된 에러 타입
        """
        if 'missing' in error_type_str:
            return ValidationErrorType.MISSING_REQUIRED_FIELD
        elif any(
            type_keyword in error_type_str
            for type_keyword in ['type', 'string', 'int', 'float', 'bool']
        ):
            return ValidationErrorType.INVALID_DATA_TYPE
        elif any(
            range_keyword in error_type_str
            for range_keyword in [
                'greater_than',
                'less_than',
                'too_short',
                'too_long',
                'value_error',
            ]
        ):
            return ValidationErrorType.VALUE_OUT_OF_RANGE
        elif 'assertion' in error_type_str or 'value_error' in error_type_str:
            return ValidationErrorType.VALIDATION_RULE_FAILED
        else:
            return ValidationErrorType.INVALID_JSON_FORMAT

    def _attempt_recovery(
        self,
        original_data: dict[str, Any],
        model_class: type[T],
        error_info: dict[str, Any],
    ) -> T | None:
        """
        데이터 복구를 시도합니다.

        Args:
            original_data: 원본 데이터
            model_class: Pydantic 모델 클래스
            error_info: 에러 정보

        Returns:
            복구된 모델 인스턴스 또는 None
        """
        error_type = error_info['error_type']
        field_path = error_info['field_path']

        # 복구 전략별 처리
        if error_type == ValidationErrorType.MISSING_REQUIRED_FIELD:
            return self._recover_missing_field(
                original_data, model_class, field_path
            )
        elif error_type == ValidationErrorType.INVALID_DATA_TYPE:
            return self._recover_invalid_type(
                original_data, model_class, field_path
            )
        elif error_type == ValidationErrorType.VALUE_OUT_OF_RANGE:
            return self._recover_out_of_range(
                original_data, model_class, field_path
            )
        else:
            # 기본값으로 대체 시도
            return self._recover_with_defaults(model_class)

    def _recover_missing_field(
        self, data: dict[str, Any], model_class: type[T], field_path: str
    ) -> T | None:
        """누락된 필드를 기본값으로 복구합니다."""
        try:
            # 기본값으로 모델 생성 시도
            return model_class()
        except ValidationError:
            return None

    def _recover_invalid_type(
        self, data: dict[str, Any], model_class: type[T], field_path: str
    ) -> T | None:
        """잘못된 타입을 제거하고 복구를 시도합니다."""
        try:
            # 문제가 있는 필드 제거
            cleaned_data = data.copy()
            if '.' in field_path:
                # 중첩된 필드 처리는 복잡하므로 일단 패스
                return None
            else:
                cleaned_data.pop(field_path, None)

            return model_class(**cleaned_data)
        except ValidationError:
            return None

    def _recover_out_of_range(
        self, data: dict[str, Any], model_class: type[T], field_path: str
    ) -> T | None:
        """범위를 벗어난 값을 제거하고 복구를 시도합니다."""
        try:
            # 문제가 있는 필드 제거
            cleaned_data = data.copy()
            if '.' not in field_path:
                cleaned_data.pop(field_path, None)

            return model_class(**cleaned_data)
        except ValidationError:
            return None

    def _recover_with_defaults(self, model_class: type[T]) -> T | None:
        """완전히 기본값으로 모델을 생성합니다."""
        try:
            return model_class()
        except ValidationError:
            return None


class ValidationReportGenerator:
    """검증 결과 리포트 생성기."""

    def __init__(self) -> None:
        """리포트 생성기 초기화."""
        self.results: list[ValidationResult] = []

    def add_result(self, result: ValidationResult, data_type: str) -> None:
        """
        검증 결과를 추가합니다.

        Args:
            result: 검증 결과
            data_type: 데이터 타입 이름
        """
        result.data_type = data_type  # type: ignore[attr-defined]
        self.results.append(result)

    def generate_summary(self) -> dict[str, Any]:
        """
        검증 결과 요약을 생성합니다.

        Returns:
            검증 결과 요약
        """
        total_count = len(self.results)
        valid_count = sum(1 for result in self.results if result.is_valid)
        recovery_count = sum(
            1 for result in self.results if result.recovery_used
        )

        error_types = {}
        for result in self.results:
            if not result.is_valid or result.recovery_used:
                error_type = (
                    result.error_type.display_name
                    if result.error_type
                    else '알 수 없음'
                )
                error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            'total_validations': total_count,
            'successful_validations': valid_count,
            'failed_validations': total_count - valid_count,
            'recovered_validations': recovery_count,
            'success_rate': valid_count / total_count
            if total_count > 0
            else 0.0,
            'error_type_counts': error_types,
            'validation_results': [
                {
                    'data_type': getattr(result, 'data_type', 'unknown'),
                    'is_valid': result.is_valid,
                    'recovery_used': result.recovery_used,
                    'error_type': (
                        result.error_type.display_name
                        if result.error_type
                        else None
                    ),
                    'field_path': result.field_path,
                    'error_message': result.error_message,
                }
                for result in self.results
            ],
        }

    def save_report(self, output_path: Path) -> None:
        """
        검증 리포트를 파일로 저장합니다.

        Args:
            output_path: 출력 파일 경로
        """
        import json

        summary = self.generate_summary()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    def clear_results(self) -> None:
        """저장된 검증 결과를 모두 제거합니다."""
        self.results.clear()

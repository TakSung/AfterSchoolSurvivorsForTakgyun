"""
JSON 스키마 검증 시스템 유닛 테스트.

이 모듈은 JSON 데이터 검증, 에러 처리, 복구 전략 등의
핵심 기능을 검증합니다.
"""

from src.data.models import (
    BossesConfig,
    EnemiesConfig,
    GameBalanceData,
    GameConfig,
    ItemsConfig,
)
from src.data.validator import (
    JsonDataValidator,
    ValidationErrorType,
    ValidationReportGenerator,
    ValidationResult,
)


class TestValidationErrorType:
    """ValidationErrorType enum 테스트."""

    def test_에러_타입_값_정확성_검증_성공_시나리오(self) -> None:
        """1. 에러 타입 enum 값들의 정확성 검증 (성공 시나리오)."""
        # Given & When & Then - enum 값 검증
        assert ValidationErrorType.INVALID_JSON_FORMAT == 0
        assert ValidationErrorType.MISSING_REQUIRED_FIELD == 1
        assert ValidationErrorType.INVALID_DATA_TYPE == 2
        assert ValidationErrorType.VALUE_OUT_OF_RANGE == 3
        assert ValidationErrorType.VALIDATION_RULE_FAILED == 4

    def test_에러_타입_표시명_정확성_검증_성공_시나리오(self) -> None:
        """2. 에러 타입 한글 표시명 정확성 검증 (성공 시나리오)."""
        # Given & When & Then - 표시명 검증
        assert (
            ValidationErrorType.INVALID_JSON_FORMAT.display_name
            == 'JSON 형식 오류'
        )
        assert (
            ValidationErrorType.MISSING_REQUIRED_FIELD.display_name
            == '필수 필드 누락'
        )
        assert (
            ValidationErrorType.INVALID_DATA_TYPE.display_name
            == '잘못된 데이터 타입'
        )
        assert (
            ValidationErrorType.VALUE_OUT_OF_RANGE.display_name
            == '값 범위 초과'
        )
        assert (
            ValidationErrorType.VALIDATION_RULE_FAILED.display_name
            == '검증 규칙 실패'
        )


class TestValidationResult:
    """ValidationResult 클래스 테스트."""

    def test_검증_성공_결과_생성_정확성_검증_성공_시나리오(self) -> None:
        """3. 검증 성공 결과 생성 정확성 검증 (성공 시나리오)."""
        # Given & When
        test_data = {'test': 'data'}
        result = ValidationResult(is_valid=True, data=test_data)

        # Then
        assert result.is_valid is True
        assert result.data == test_data
        assert result.error_type is None
        assert result.error_message == ''
        assert result.field_path == ''
        assert result.recovery_used is False

    def test_검증_실패_결과_생성_정확성_검증_성공_시나리오(self) -> None:
        """4. 검증 실패 결과 생성 정확성 검증 (성공 시나리오)."""
        # Given & When
        result = ValidationResult(
            is_valid=False,
            error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
            error_message='필드가 누락됨',
            field_path='weapons.soccer_ball',
        )

        # Then
        assert result.is_valid is False
        assert result.data is None
        assert result.error_type == ValidationErrorType.MISSING_REQUIRED_FIELD
        assert result.error_message == '필드가 누락됨'
        assert result.field_path == 'weapons.soccer_ball'
        assert result.recovery_used is False

    def test_복구_사용_결과_표현_정확성_검증_성공_시나리오(self) -> None:
        """5. 복구 사용 결과 표현 정확성 검증 (성공 시나리오)."""
        # Given & When
        result = ValidationResult(
            is_valid=True,
            data={'recovered': True},
            recovery_used=True,
        )

        # Then
        assert result.is_valid is True
        assert result.recovery_used is True
        assert '복구됨' in str(result)


class TestJsonDataValidator:
    """JsonDataValidator 클래스 테스트."""

    def test_검증기_초기화_설정_정확성_검증_성공_시나리오(self) -> None:
        """6. 검증기 초기화 설정 정확성 검증 (성공 시나리오)."""
        # Given & When - 복구 활성화
        validator_with_recovery = JsonDataValidator(enable_recovery=True)

        # Then
        assert validator_with_recovery.enable_recovery is True

        # Given & When - 복구 비활성화
        validator_without_recovery = JsonDataValidator(enable_recovery=False)

        # Then
        assert validator_without_recovery.enable_recovery is False

    def test_아이템_설정_검증_성공_시나리오(self) -> None:
        """7. 아이템 설정 검증 성공 시나리오."""
        # Given
        validator = JsonDataValidator()
        valid_items_data = {
            'weapons': {
                'soccer_ball': {
                    'weapon_type': 0,
                    'name': '축구공',
                    'base_damage': 10,
                    'attack_speed': 1.2,
                    'attack_range': 180.0,
                }
            },
            'abilities': {},
            'synergies': {},
        }

        # When
        result = validator.validate_items_config(valid_items_data)

        # Then
        assert result.is_valid is True
        assert isinstance(result.data, ItemsConfig)
        assert result.error_type is None
        assert result.recovery_used is False

    def test_아이템_설정_검증_실패_시나리오(self) -> None:
        """8. 아이템 설정 검증 실패 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=False)
        invalid_items_data = {
            'weapons': {},  # 빈 weapons 딕셔너리 (검증 실패 예상)
            'abilities': {},
            'synergies': {},
        }

        # When
        result = validator.validate_items_config(invalid_items_data)

        # Then
        assert result.is_valid is False
        assert result.error_type is not None
        assert '최소 하나의 무기가 정의되어야 합니다' in result.error_message
        assert result.recovery_used is False

    def test_적_설정_검증_성공_시나리오(self) -> None:
        """9. 적 설정 검증 성공 시나리오."""
        # Given
        validator = JsonDataValidator()
        valid_enemies_data = {
            'basic_enemies': {
                'korean_teacher': {
                    'enemy_type': 0,
                    'name': '국어 선생님',
                    'base_health': 50,
                    'base_speed': 30.0,
                    'base_attack_power': 25,
                }
            },
            'elite_enemies': {},
        }

        # When
        result = validator.validate_enemies_config(valid_enemies_data)

        # Then
        assert result.is_valid is True
        assert isinstance(result.data, EnemiesConfig)
        assert result.error_type is None

    def test_보스_설정_검증_성공_시나리오(self) -> None:
        """10. 보스 설정 검증 성공 시나리오."""
        # Given
        validator = JsonDataValidator()
        valid_bosses_data = {
            'bosses': {
                'principal': {
                    'enemy_type': 2,  # PRINCIPAL
                    'name': '교장 선생님',
                    'base_health': 500,
                    'base_speed': 50.0,
                    'base_attack_power': 100,
                }
            },
            'boss_phases': {},
        }

        # When
        result = validator.validate_bosses_config(valid_bosses_data)

        # Then
        assert result.is_valid is True
        assert isinstance(result.data, BossesConfig)

    def test_게임_밸런스_검증_성공_시나리오(self) -> None:
        """11. 게임 밸런스 검증 성공 시나리오."""
        # Given
        validator = JsonDataValidator()
        valid_balance_data = {
            'player': {
                'base_health': 100,
                'base_speed': 200.0,
                'base_attack_power': 10,
            },
            'difficulty': {
                'scaling_factor': 1.1,
                'boss_interval': 90.0,
                'max_enemies_on_screen': 50,
            },
        }

        # When
        result = validator.validate_game_balance(valid_balance_data)

        # Then
        assert result.is_valid is True
        assert isinstance(result.data, GameBalanceData)

    def test_전체_게임_설정_검증_성공_시나리오(self) -> None:
        """12. 전체 게임 설정 검증 성공 시나리오."""
        # Given
        validator = JsonDataValidator()
        complete_config = {
            'items': {
                'weapons': {
                    'soccer_ball': {
                        'weapon_type': 0,
                        'name': '축구공',
                        'base_damage': 10,
                        'attack_speed': 1.2,
                        'attack_range': 180.0,
                    }
                },
                'abilities': {},
                'synergies': {},
            },
            'enemies': {
                'basic_enemies': {
                    'korean_teacher': {
                        'enemy_type': 0,
                        'name': '국어 선생님',
                        'base_health': 50,
                        'base_speed': 30.0,
                        'base_attack_power': 25,
                    }
                },
                'elite_enemies': {},
            },
            'bosses': {
                'bosses': {
                    'principal': {
                        'enemy_type': 2,
                        'name': '교장 선생님',
                        'base_health': 500,
                        'base_speed': 50.0,
                        'base_attack_power': 100,
                    }
                },
                'boss_phases': {},
            },
            'game_balance': {},
        }

        # When
        result = validator.validate_complete_config(complete_config)

        # Then
        assert result.is_valid is True
        assert isinstance(result.data, GameConfig)

    def test_에러_분류_정확성_검증_성공_시나리오(self) -> None:
        """13. 에러 분류 정확성 검증 (성공 시나리오)."""
        # Given
        validator = JsonDataValidator()

        # When & Then - missing 에러
        error_type = validator._classify_error_type('missing', '필드 누락')
        assert error_type == ValidationErrorType.MISSING_REQUIRED_FIELD

        # type 에러
        error_type = validator._classify_error_type('type_error', 'wrong type')
        assert error_type == ValidationErrorType.INVALID_DATA_TYPE

        # range 에러
        error_type = validator._classify_error_type(
            'greater_than', 'value too small'
        )
        assert error_type == ValidationErrorType.VALUE_OUT_OF_RANGE

        # 기본 에러
        error_type = validator._classify_error_type('unknown', 'unknown error')
        assert error_type == ValidationErrorType.INVALID_JSON_FORMAT

    def test_복구_전략_기본값_생성_성공_시나리오(self) -> None:
        """14. 복구 전략 기본값 생성 성공 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)

        # When - 빈 데이터로 기본값 복구 시도
        recovered = validator._recover_with_defaults(ItemsConfig)

        # Then
        assert recovered is not None
        assert isinstance(recovered, ItemsConfig)

    def test_복구_전략_누락_필드_처리_성공_시나리오(self) -> None:
        """15. 복구 전략 누락 필드 처리 성공 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)
        incomplete_data = {'abilities': {}, 'synergies': {}}

        # When
        recovered = validator._recover_missing_field(
            incomplete_data, ItemsConfig, 'weapons'
        )

        # Then
        assert recovered is not None
        assert isinstance(recovered, ItemsConfig)

    def test_잘못된_타입_제거_복구_성공_시나리오(self) -> None:
        """16. 잘못된 타입 제거 복구 성공 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)
        invalid_data = {
            'weapons': {
                'soccer_ball': {
                    'weapon_type': 0,
                    'name': '축구공',
                    'base_damage': 10,
                    'attack_speed': 1.2,
                    'attack_range': 180.0,
                }
            },
            'abilities': {},
            'synergies': {},
            'invalid_field': 'should_be_removed',
        }

        # When
        recovered = validator._recover_invalid_type(
            invalid_data, ItemsConfig, 'invalid_field'
        )

        # Then
        assert recovered is not None
        assert isinstance(recovered, ItemsConfig)


class TestValidationReportGenerator:
    """ValidationReportGenerator 클래스 테스트."""

    def test_리포트_생성기_초기화_정확성_검증_성공_시나리오(self) -> None:
        """17. 리포트 생성기 초기화 정확성 검증 (성공 시나리오)."""
        # Given & When
        generator = ValidationReportGenerator()

        # Then
        assert isinstance(generator.results, list)
        assert len(generator.results) == 0

    def test_검증_결과_추가_정확성_검증_성공_시나리오(self) -> None:
        """18. 검증 결과 추가 정확성 검증 (성공 시나리오)."""
        # Given
        generator = ValidationReportGenerator()
        result = ValidationResult(is_valid=True, data={'test': 'data'})

        # When
        generator.add_result(result, 'items')

        # Then
        assert len(generator.results) == 1
        assert hasattr(result, 'data_type')
        assert result.data_type == 'items'  # type: ignore[attr-defined]

    def test_검증_요약_생성_정확성_검증_성공_시나리오(self) -> None:
        """19. 검증 요약 생성 정확성 검증 (성공 시나리오)."""
        # Given
        generator = ValidationReportGenerator()

        # 성공 결과 추가
        success_result = ValidationResult(is_valid=True, data={'test': 'data'})
        generator.add_result(success_result, 'items')

        # 실패 결과 추가
        fail_result = ValidationResult(
            is_valid=False,
            error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
            error_message='필드 누락',
            field_path='weapons',
        )
        generator.add_result(fail_result, 'enemies')

        # 복구 결과 추가
        recovery_result = ValidationResult(
            is_valid=True,
            data={'recovered': True},
            error_type=ValidationErrorType.INVALID_DATA_TYPE,
            error_message='타입 오류',
            field_path='bosses',
            recovery_used=True,
        )
        generator.add_result(recovery_result, 'bosses')

        # When
        summary = generator.generate_summary()

        # Then
        assert summary['total_validations'] == 3
        assert summary['successful_validations'] == 2
        assert summary['failed_validations'] == 1
        assert summary['recovered_validations'] == 1
        assert summary['success_rate'] == 2 / 3

        # 에러 타입 개수 확인
        error_counts = summary['error_type_counts']
        assert '필수 필드 누락' in error_counts
        assert '잘못된 데이터 타입' in error_counts

        # 개별 결과 확인
        results = summary['validation_results']
        assert len(results) == 3
        assert results[0]['data_type'] == 'items'
        assert results[0]['is_valid'] is True

    def test_결과_초기화_정확성_검증_성공_시나리오(self) -> None:
        """20. 결과 초기화 정확성 검증 (성공 시나리오)."""
        # Given
        generator = ValidationReportGenerator()
        result = ValidationResult(is_valid=True, data={'test': 'data'})
        generator.add_result(result, 'items')

        # When
        generator.clear_results()

        # Then
        assert len(generator.results) == 0

    def test_빈_결과_요약_생성_정확성_검증_성공_시나리오(self) -> None:
        """21. 빈 결과 요약 생성 정확성 검증 (성공 시나리오)."""
        # Given
        generator = ValidationReportGenerator()

        # When
        summary = generator.generate_summary()

        # Then
        assert summary['total_validations'] == 0
        assert summary['successful_validations'] == 0
        assert summary['failed_validations'] == 0
        assert summary['recovered_validations'] == 0
        assert summary['success_rate'] == 0.0
        assert summary['error_type_counts'] == {}
        assert summary['validation_results'] == []


class TestValidationIntegration:
    """검증 시스템 통합 테스트."""

    def test_복구_활성화_검증_통합_시나리오(self) -> None:
        """22. 복구 활성화 검증 통합 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)
        generator = ValidationReportGenerator()

        # 의도적으로 실패할 데이터
        invalid_data = {'weapons': {}, 'abilities': {}, 'synergies': {}}

        # When
        result = validator.validate_items_config(invalid_data)
        generator.add_result(result, 'items')

        # Then
        # 복구 시도로 인해 성공할 수 있음
        if result.is_valid:
            assert result.recovery_used is True
        else:
            assert result.error_type is not None

        summary = generator.generate_summary()
        assert summary['total_validations'] == 1

    def test_복구_비활성화_검증_통합_시나리오(self) -> None:
        """23. 복구 비활성화 검증 통합 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=False)
        generator = ValidationReportGenerator()

        # 의도적으로 실패할 데이터
        invalid_data = {'weapons': {}, 'abilities': {}, 'synergies': {}}

        # When
        result = validator.validate_items_config(invalid_data)
        generator.add_result(result, 'items')

        # Then
        assert result.is_valid is False
        assert result.recovery_used is False
        assert result.error_type is not None

        summary = generator.generate_summary()
        assert summary['total_validations'] == 1
        assert summary['successful_validations'] == 0
        assert summary['failed_validations'] == 1

    def test_다중_데이터_타입_검증_통합_시나리오(self) -> None:
        """24. 다중 데이터 타입 검증 통합 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)
        generator = ValidationReportGenerator()

        # 각 타입별 유효한 데이터
        valid_items = {
            'weapons': {
                'soccer_ball': {
                    'weapon_type': 0,
                    'name': '축구공',
                    'base_damage': 10,
                    'attack_speed': 1.2,
                    'attack_range': 180.0,
                }
            },
            'abilities': {},
            'synergies': {},
        }

        valid_enemies = {
            'basic_enemies': {
                'korean_teacher': {
                    'enemy_type': 0,
                    'name': '국어 선생님',
                    'base_health': 50,
                    'base_speed': 30.0,
                    'base_attack_power': 25,
                }
            },
            'elite_enemies': {},
        }

        valid_bosses = {
            'bosses': {
                'principal': {
                    'enemy_type': 2,
                    'name': '교장 선생님',
                    'base_health': 500,
                    'base_speed': 50.0,
                    'base_attack_power': 100,
                }
            },
            'boss_phases': {},
        }

        valid_balance = {}

        # When
        items_result = validator.validate_items_config(valid_items)
        enemies_result = validator.validate_enemies_config(valid_enemies)
        bosses_result = validator.validate_bosses_config(valid_bosses)
        balance_result = validator.validate_game_balance(valid_balance)

        generator.add_result(items_result, 'items')
        generator.add_result(enemies_result, 'enemies')
        generator.add_result(bosses_result, 'bosses')
        generator.add_result(balance_result, 'balance')

        # Then
        summary = generator.generate_summary()
        assert summary['total_validations'] == 4
        assert summary['successful_validations'] == 4
        assert summary['success_rate'] == 1.0

    def test_에러_파싱_및_복구_전략_통합_시나리오(self) -> None:
        """25. 에러 파싱 및 복구 전략 통합 시나리오."""
        # Given
        validator = JsonDataValidator(enable_recovery=True)

        # 복잡한 검증 실패 데이터
        complex_invalid_data = {
            'weapons': {
                'invalid_weapon': {
                    'weapon_type': 999,  # 유효하지 않은 enum 값
                    'name': '',  # 빈 이름
                    'base_damage': -10,  # 음수 데미지
                    'attack_speed': 'invalid',  # 잘못된 타입
                    'attack_range': 0,  # 0 범위
                }
            },
            'abilities': {},
            'synergies': {},
        }

        # When
        result = validator.validate_items_config(complex_invalid_data)

        # Then
        # 검증 실패 또는 복구 성공 중 하나
        if result.is_valid:
            assert result.recovery_used is True
        else:
            assert result.error_type is not None
            assert result.error_message != ''
            assert result.field_path != ''

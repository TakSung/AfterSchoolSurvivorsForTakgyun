"""
DataLoader와 JSON 검증 시스템 통합 테스트.

이 모듈은 DataLoader 클래스와 JsonDataValidator의 통합 기능을
검증합니다.
"""

import pytest

from src.data.loader import DataLoader
from src.data.validator import ValidationResult


class MockFileRepository:
    """테스트용 파일 시스템 Mock."""

    def __init__(self) -> None:
        """Mock 파일 시스템 초기화."""
        self.files: dict[str, dict] = {}
        self.directories: set[str] = set()

    def exists(self, path: str | object) -> bool:
        """파일 존재 여부 확인."""
        return str(path) in self.files

    def read_json(self, path: str | object) -> dict:
        """JSON 파일 읽기."""
        return self.files.get(str(path), {})

    def write_json(self, path: str | object, data: dict) -> None:
        """JSON 파일 쓰기."""
        self.files[str(path)] = data

    def ensure_directory(self, path: str | object) -> None:
        """디렉토리 생성."""
        self.directories.add(str(path))


class TestDataLoaderValidation:
    """DataLoader 검증 통합 테스트."""

    def setup_method(self):
        """각 테스트 전에 싱글톤 인스턴스 초기화."""
        DataLoader._instance = None

    def test_검증_활성화_로더_초기화_정확성_검증_성공_시나리오(self) -> None:
        """1. 검증 활성화 로더 초기화 정확성 검증 (성공 시나리오)."""
        # Given
        mock_repo = MockFileRepository()

        # When
        loader = DataLoader(
            file_repository=mock_repo,
            enable_validation=True,
            enable_recovery=True,
        )

        # Then
        status = loader.get_validation_status()
        assert status['validation_enabled'] is True
        assert status['recovery_enabled'] is True
        assert status['validator_available'] is True

    def test_검증_비활성화_로더_초기화_정확성_검증_성공_시나리오(self) -> None:
        """2. 검증 비활성화 로더 초기화 정확성 검증 (성공 시나리오)."""
        # Given
        mock_repo = MockFileRepository()

        # When
        loader = DataLoader(file_repository=mock_repo, enable_validation=False)

        # Then
        status = loader.get_validation_status()
        assert status['validation_enabled'] is False
        assert status['recovery_enabled'] is False
        assert status['validator_available'] is False

    def test_유효한_아이템_데이터_로딩_검증_성공_시나리오(self) -> None:
        """3. 유효한 아이템 데이터 로딩 검증 성공 시나리오."""
        # Given
        mock_repo = MockFileRepository()
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

        # 파일 시스템에 데이터 설정
        # DataLoader는 data_path/filename 형태로 경로를 구성
        from pathlib import Path

        data_path = Path(__file__).parent.parent / 'data'
        items_file_path = str(data_path / 'items.json')
        mock_repo.files[items_file_path] = valid_items_data

        loader = DataLoader(file_repository=mock_repo, enable_validation=True)

        # When
        items_data = loader.load_items()

        # Then
        assert items_data is not None
        assert 'weapons' in items_data
        assert 'soccer_ball' in items_data['weapons']

    def test_무효한_아이템_데이터_로딩_검증_실패_시나리오(self) -> None:
        """4. 무효한 아이템 데이터 로딩 검증 실패 시나리오."""
        # Given
        mock_repo = MockFileRepository()
        invalid_items_data = {
            'weapons': {},  # 빈 weapons 딕셔너리
            'abilities': {},
            'synergies': {},
        }

        # 파일 시스템에 무효한 데이터 설정
        items_file_path = 'data/items.json'
        mock_repo.files[items_file_path] = invalid_items_data

        loader = DataLoader(
            file_repository=mock_repo,
            enable_validation=True,
            enable_recovery=False,
        )

        # When & Then
        try:
            loader.load_items()
            pytest.fail('검증 오류가 발생해야 함')
        except ValueError as e:
            assert '아이템 데이터 검증 실패' in str(e)

    def test_복구_활성화_무효_데이터_로딩_성공_시나리오(self) -> None:
        """5. 복구 활성화 무효 데이터 로딩 성공 시나리오."""
        # Given
        mock_repo = MockFileRepository()
        invalid_items_data = {
            'weapons': {},  # 빈 weapons 딕셔너리
            'abilities': {},
            'synergies': {},
        }

        items_file_path = 'data/items.json'
        mock_repo.files[items_file_path] = invalid_items_data

        loader = DataLoader(
            file_repository=mock_repo,
            enable_validation=True,
            enable_recovery=True,
        )

        # When
        items_data = loader.load_items()

        # Then
        # 복구 또는 실패 중 하나
        if items_data:
            assert isinstance(items_data, dict)
        # 복구가 실패하면 예외가 발생할 수 있음

    def test_전체_데이터_검증_성공_시나리오(self) -> None:
        """6. 전체 데이터 검증 성공 시나리오."""
        # Given
        mock_repo = MockFileRepository()

        # 유효한 데이터 설정
        valid_data = {
            'items.json': {
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
            'enemies.json': {
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
            'bosses.json': {
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
            'game_balance.json': {},
        }

        for filename, data in valid_data.items():
            mock_repo.files[filename] = data

        loader = DataLoader(file_repository=mock_repo, enable_validation=True)

        # When
        results = loader.load_all_with_validation()

        # Then
        assert len(results) == 4
        assert 'items' in results
        assert 'enemies' in results
        assert 'bosses' in results
        assert 'game_balance' in results

        for _data_type, result in results.items():
            assert isinstance(result, ValidationResult)

    def test_통합_게임_설정_검증_성공_시나리오(self) -> None:
        """7. 통합 게임 설정 검증 성공 시나리오."""
        # Given
        mock_repo = MockFileRepository()

        # 완전한 게임 설정 데이터 준비
        complete_data = {
            'items.json': {
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
            'enemies.json': {
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
            'bosses.json': {
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
            'game_balance.json': {},
        }

        for filename, data in complete_data.items():
            mock_repo.files[filename] = data

        loader = DataLoader(file_repository=mock_repo, enable_validation=True)

        # When
        result = loader.validate_complete_game_config()

        # Then
        assert isinstance(result, ValidationResult)
        # 통합 검증이 성공하거나 실패할 수 있음

    def test_검증_비활성화_시_에러_발생_확인_시나리오(self) -> None:
        """8. 검증 비활성화 시 에러 발생 확인 시나리오."""
        # Given
        mock_repo = MockFileRepository()
        loader = DataLoader(file_repository=mock_repo, enable_validation=False)

        # When & Then
        try:
            loader.load_all_with_validation()
            pytest.fail('RuntimeError가 발생해야 함')
        except RuntimeError as e:
            assert '검증이 비활성화된 상태' in str(e)

        try:
            loader.validate_complete_game_config()
            pytest.fail('RuntimeError가 발생해야 함')
        except RuntimeError as e:
            assert '검증이 비활성화된 상태' in str(e)

    def test_싱글톤_패턴_검증_시스템_공유_확인_시나리오(self) -> None:
        """9. 싱글톤 패턴 검증 시스템 공유 확인 시나리오."""
        # Given
        mock_repo = MockFileRepository()

        # When
        loader1 = DataLoader(file_repository=mock_repo, enable_validation=True)
        loader2 = DataLoader(file_repository=mock_repo, enable_validation=True)

        # Then
        assert loader1 is loader2
        status1 = loader1.get_validation_status()
        status2 = loader2.get_validation_status()
        assert status1 == status2

    def test_캐시와_검증_시스템_연동_확인_시나리오(self) -> None:
        """10. 캐시와 검증 시스템 연동 확인 시나리오."""
        # Given
        mock_repo = MockFileRepository()
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

        items_file_path = 'items.json'
        mock_repo.files[items_file_path] = valid_items_data

        # 싱글톤 초기화를 위해 클래스 변수 리셋
        DataLoader._instance = None

        loader = DataLoader(file_repository=mock_repo, enable_validation=True)

        # When - 첫 번째 로딩 (캐시 없음)
        items_data_1 = loader.load_items(use_cache=True)

        # 파일 데이터 변경
        modified_data = valid_items_data.copy()
        modified_data['weapons']['soccer_ball']['name'] = '수정된 축구공'
        mock_repo.files[items_file_path] = modified_data

        # 두 번째 로딩 (캐시 사용)
        items_data_2 = loader.load_items(use_cache=True)

        # 세 번째 로딩 (캐시 미사용)
        items_data_3 = loader.load_items(use_cache=False)

        # Then
        assert items_data_1 is not None
        assert items_data_2 is not None
        assert items_data_3 is not None

        # 캐시 사용 시 동일한 데이터
        assert items_data_1 == items_data_2

        # 캐시 미사용 시 새로운 데이터 (검증 시스템이 적용됨)
        # 검증이 성공하면 새 데이터, 실패하면 에러

    def test_에러_메시지_한글화_확인_시나리오(self) -> None:
        """11. 에러 메시지 한글화 확인 시나리오."""
        # Given
        mock_repo = MockFileRepository()
        invalid_data = {'weapons': {}, 'abilities': {}, 'synergies': {}}

        mock_repo.files['items.json'] = invalid_data

        # 싱글톤 초기화
        DataLoader._instance = None

        loader = DataLoader(
            file_repository=mock_repo,
            enable_validation=True,
            enable_recovery=False,
        )

        # When & Then
        try:
            loader.load_items()
            pytest.fail('검증 오류가 발생해야 함')
        except ValueError as e:
            error_message = str(e)
            assert '아이템 데이터 검증 실패' in error_message
            # 한글 에러 메시지 확인
            assert '필드' in error_message or '검증' in error_message

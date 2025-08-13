"""
DataLoader 클래스에 대한 유닛 테스트.

Repository 패턴을 적용한 DataLoader의 JSON 파일 로딩, 캐싱,
싱글톤 패턴 등의 핵심 기능을 검증합니다.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from src.data.file_repository import IFileRepository
from src.data.loader import DataLoader


class MockFileRepository(IFileRepository):
    """테스트용 Mock File Repository 구현체."""

    def __init__(self):
        self.exists_return_value = True
        self.read_json_return_value = {'test': 'data'}
        self.exists_calls = []
        self.read_json_calls = []
        self.write_json_calls = []
        self.ensure_directory_calls = []

        # 예외 발생 설정
        self.should_raise_permission_error = False
        self.should_raise_file_not_found = False
        self.should_raise_json_decode_error = False

    def exists(self, file_path: Path) -> bool:
        self.exists_calls.append(file_path)
        return self.exists_return_value

    def read_json(self, file_path: Path) -> dict[str, Any]:
        self.read_json_calls.append(file_path)

        if self.should_raise_permission_error:
            raise PermissionError('Cannot read file')
        if self.should_raise_file_not_found:
            raise FileNotFoundError('File not found')
        if self.should_raise_json_decode_error:
            raise json.JSONDecodeError('Invalid JSON', '', 0)

        return self.read_json_return_value

    def write_json(self, file_path: Path, data: dict[str, Any]) -> None:
        self.write_json_calls.append((file_path, data))

    def ensure_directory(self, directory_path: Path) -> None:
        self.ensure_directory_calls.append(directory_path)


class TestDataLoader:
    """DataLoader 클래스 테스트 클래스."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """각 테스트마다 싱글톤 인스턴스를 초기화."""
        DataLoader._instance = None
        yield
        DataLoader._instance = None

    @pytest.fixture
    def mock_repository(self):
        """Mock File Repository 픽스처."""
        return MockFileRepository()

    @pytest.fixture
    def data_loader(self, mock_repository):
        """Mock Repository를 주입한 DataLoader 픽스처."""
        # 기존 테스트와의 호환성을 위해 검증 비활성화
        return DataLoader(mock_repository, enable_validation=False)

    def test_새_파일_로딩_시_기본_데이터_생성_및_캐싱_검증_성공_시나리오(
        self, mock_repository, data_loader
    ):
        """1. 새 파일 로딩 시 기본 데이터 생성 및 캐싱 검증 (성공 시나리오)

        목적: 파일이 존재하지 않을 때 기본 데이터 구조 생성 및 캐시 저장 검증
        테스트할 범위: load_json의 파일 생성 로직 및 캐싱 메커니즘
        커버하는 함수 및 데이터: load_items, _get_default_data, 캐시 저장
        기대되는 안정성: 파일 부재 시에도 안정적인 기본값 제공
        """
        # Given - items.json이 존재하지 않는 상황 설정
        mock_repository.exists_return_value = False

        # When - items 데이터 로딩
        result = data_loader.load_items(use_cache=True)

        # Then - 기본 구조 반환 확인
        expected_default = {'weapons': {}, 'abilities': {}, 'synergies': {}}
        assert result == expected_default, '기본 items 구조가 정확해야 함'

        # Then - write_json 호출 확인
        assert len(mock_repository.write_json_calls) == 1, (
            '기본 데이터 파일 생성해야 함'
        )
        written_path, written_data = mock_repository.write_json_calls[0]
        assert 'items.json' in str(written_path), 'items.json 파일 경로여야 함'
        assert written_data == expected_default, (
            '기본 데이터가 파일에 저장되어야 함'
        )

        # Then - 캐시 저장 확인
        assert data_loader.is_cached('items.json'), (
            '데이터가 캐시에 저장되어야 함'
        )

    def test_기존_파일_로딩_및_캐시_활용_검증_성공_시나리오(
        self, mock_repository, data_loader
    ):
        """2. 기존 파일 로딩 및 캐시 활용 검증 (성공 시나리오)

        목적: 파일이 존재할 때 로딩 및 두 번째 호출 시 캐시 사용 검증
        테스트할 범위: load_json의 파일 읽기 및 캐시 메커니즘
        커버하는 함수 및 데이터: load_enemies, 캐시 hit/miss 로직
        기대되는 안정성: 캐시를 통한 성능 최적화 및 일관된 데이터 제공
        """
        # Given - enemies.json이 존재하고 유효한 데이터 설정
        mock_repository.exists_return_value = True
        expected_data = {
            'basic_enemies': {'orc': {'hp': 100}},
            'elite_enemies': {},
        }
        mock_repository.read_json_return_value = expected_data

        # When - enemies 데이터를 두 번 연속 로딩
        result1 = data_loader.load_enemies(use_cache=True)
        result2 = data_loader.load_enemies(use_cache=True)

        # Then - 동일한 데이터 반환 확인
        assert result1 == expected_data, '첫 번째 로딩 결과가 정확해야 함'
        assert result2 == expected_data, '두 번째 로딩 결과가 정확해야 함'
        assert result1 is result2, '캐시된 동일한 객체 참조여야 함'

        # Then - 파일 읽기가 한 번만 호출되었는지 확인
        assert len(mock_repository.read_json_calls) == 1, (
            '파일은 한 번만 읽어야 함'
        )

        # Then - 캐시 상태 확인
        assert data_loader.is_cached('enemies.json'), (
            '데이터가 캐시에 저장되어야 함'
        )

    def test_싱글톤_패턴_정확성_검증_성공_시나리오(self, reset_singleton):
        """3. 싱글톤 패턴 정확성 검증 (성공 시나리오)

        목적: 여러 번 DataLoader 생성 시 동일한 인스턴스 반환 검증
        테스트할 범위: __new__ 메서드의 싱글톤 구현
        커버하는 함수 및 데이터: 인스턴스 생성 및 _instance 클래스 변수
        기대되는 안정성: 애플리케이션 전체에서 단일 DataLoader 인스턴스 보장
        """
        # Given - 두 개의 서로 다른 Mock Repository
        mock_repo1 = MockFileRepository()
        mock_repo2 = MockFileRepository()

        # When - DataLoader를 두 번 생성
        loader1 = DataLoader(mock_repo1)
        loader2 = DataLoader(mock_repo2)

        # Then - 동일한 인스턴스 반환 확인
        assert loader1 is loader2, '싱글톤으로 동일한 인스턴스여야 함'

        # Then - 첫 번째 repository만 사용됨 확인
        loader1.load_items()
        assert len(mock_repo1.ensure_directory_calls) > 0, (
            '첫 번째 repository가 사용되어야 함'
        )
        assert len(mock_repo2.ensure_directory_calls) == 0, (
            '두 번째 repository는 사용되지 않아야 함'
        )

    def test_filename_타입_오류_처리_검증_실패_시나리오(self, data_loader):
        """4. filename 타입 오류 처리 검증 (실패 시나리오)

        목적: 잘못된 타입의 filename 입력 시 적절한 예외 발생 검증
        테스트할 범위: load_json의 타입 검증 로직
        커버하는 함수 및 데이터: isinstance 검사 및 TypeError 발생
        기대되는 안정성: 잘못된 입력에 대한 명확한 오류 메시지 제공
        """
        # Given - 잘못된 타입의 filename들
        invalid_filenames = [None, 123, [], {}, True, 3.14]

        for invalid_filename in invalid_filenames:
            # When & Then - TypeError 발생 확인
            with pytest.raises(TypeError) as exc_info:
                data_loader.load_json(invalid_filename)

            # Then - 적절한 오류 메시지 확인
            error_message = str(exc_info.value)
            assert 'Expected str for filename' in error_message, (
                f'적절한 오류 메시지여야 함: {invalid_filename}'
            )
            assert str(type(invalid_filename)) in error_message, (
                f'타입 정보가 포함되어야 함: {invalid_filename}'
            )

    def test_set_data_path_타입_오류_처리_검증_실패_시나리오(
        self, data_loader
    ):
        """5. set_data_path 타입 오류 처리 검증 (실패 시나리오)

        목적: 잘못된 타입의 path 입력 시 적절한 예외 발생 검증
        테스트할 범위: set_data_path의 타입 검증 로직
        커버하는 함수 및 데이터: isinstance 검사 및 TypeError 발생
        기대되는 안정성: 경로 설정 시 타입 안전성 보장
        """
        # Given - 잘못된 타입의 path들
        invalid_paths = [None, 123, [], {}, True]

        for invalid_path in invalid_paths:
            # When & Then - TypeError 발생 확인
            with pytest.raises(TypeError) as exc_info:
                data_loader.set_data_path(invalid_path)

            # Then - 적절한 오류 메시지 확인
            error_message = str(exc_info.value)
            assert 'Expected str or Path' in error_message, (
                f'적절한 오류 메시지여야 함: {invalid_path}'
            )
            assert str(type(invalid_path)) in error_message, (
                f'타입 정보가 포함되어야 함: {invalid_path}'
            )

    def test_파일_시스템_예외_전파_검증_실패_시나리오(
        self, mock_repository, data_loader
    ):
        """6. 파일 시스템 예외 전파 검증 (실패 시나리오)

        목적: Repository에서 발생한 예외가 적절히 전파되는지 검증
        테스트할 범위: 예외 처리 및 전파 로직
        커버하는 함수 및 데이터: PermissionError, FileNotFoundError 전파
        기대되는 안정성: 파일 시스템 오류 시 명확한 예외 정보 제공
        """
        # Given - 파일이 존재하도록 설정
        mock_repository.exists_return_value = True

        # When & Then - PermissionError 전파 확인
        mock_repository.should_raise_permission_error = True
        with pytest.raises(PermissionError):
            data_loader.load_json('test.json')

        # When & Then - FileNotFoundError 전파 확인
        mock_repository.should_raise_permission_error = False
        mock_repository.should_raise_file_not_found = True
        with pytest.raises(FileNotFoundError):
            data_loader.load_json('test.json')

    def test_캐시_무효화_동작_검증_성공_시나리오(
        self, mock_repository, data_loader
    ):
        """7. 캐시 무효화 동작 검증 (성공 시나리오)

        목적: 캐시 초기화 및 경로 변경 시 캐시 무효화 동작 검증
        테스트할 범위: clear_cache, set_data_path의 캐시 관리 로직
        커버하는 함수 및 데이터: 캐시 상태 변화 및 재로딩 동작
        기대되는 안정성: 데이터 일관성을 위한 캐시 관리 정확성
        """
        # Given - 데이터를 캐시에 로딩
        mock_repository.exists_return_value = True
        mock_repository.read_json_return_value = {'cached': 'data'}
        data_loader.load_json('test.json', use_cache=True)

        # Then - 캐시된 상태 확인
        assert data_loader.is_cached('test.json'), '데이터가 캐시되어야 함'

        # When - 캐시 수동 무효화
        data_loader.clear_cache()

        # Then - 캐시 무효화 확인
        assert not data_loader.is_cached('test.json'), '캐시가 무효화되어야 함'

        # Given - 다시 캐시에 로딩
        data_loader.load_json('test.json', use_cache=True)
        assert data_loader.is_cached('test.json'), (
            '데이터가 다시 캐시되어야 함'
        )

        # When - 데이터 경로 변경으로 캐시 무효화
        data_loader.set_data_path('/new/path')

        # Then - 경로 변경으로 캐시 무효화 확인
        assert not data_loader.is_cached('test.json'), (
            '경로 변경 시 캐시가 무효화되어야 함'
        )

    def test_특정_파일_타입별_로딩_메서드_검증_성공_시나리오(
        self, mock_repository, data_loader
    ):
        """8. 특정 파일 타입별 로딩 메서드 검증 (성공 시나리오)

        목적: load_items, load_enemies, load_bosses, load_game_balance 메서드 검증
        테스트할 범위: 각 메서드가 올바른 파일명으로 load_json 호출하는지 확인
        커버하는 함수 및 데이터: 파일명 매핑 및 메서드 위임
        기대되는 안정성: 각 게임 데이터 타입별 정확한 파일 로딩
        """
        # Given - 각 파일이 존재하고 고유한 데이터 설정
        mock_repository.exists_return_value = True

        test_cases = [
            ('load_items', 'items.json', {'weapons': {'sword': {}}}),
            (
                'load_enemies',
                'enemies.json',
                {'basic_enemies': {'goblin': {}}},
            ),
            ('load_bosses', 'bosses.json', {'bosses': {'dragon': {}}}),
            (
                'load_game_balance',
                'game_balance.json',
                {'player': {'hp': 100}},
            ),
        ]

        for method_name, expected_filename, test_data in test_cases:
            # Given - 특정 데이터 설정
            mock_repository.read_json_return_value = test_data
            mock_repository.read_json_calls.clear()

            # When - 해당 메서드 호출
            method = getattr(data_loader, method_name)
            result = method()

            # Then - 올바른 결과 및 파일 호출 확인
            assert result == test_data, (
                f'{method_name}이 올바른 데이터를 반환해야 함'
            )
            assert len(mock_repository.read_json_calls) == 1, (
                f'{method_name}이 파일을 읽어야 함'
            )
            called_path = mock_repository.read_json_calls[0]
            assert expected_filename in str(called_path), (
                f'{method_name}이 {expected_filename}을 호출해야 함'
            )

    def test_reload_all_동작_검증_성공_시나리오(
        self, mock_repository, data_loader
    ):
        """9. reload_all 동작 검증 (성공 시나리오)

        목적: 전체 데이터 리로딩 시 캐시 초기화 및 모든 파일 재로딩 검증
        테스트할 범위: reload_all 메서드의 전체 리로딩 로직
        커버하는 함수 및 데이터: 캐시 초기화 및 모든 데이터 타입 로딩
        기대되는 안정성: 데이터 일관성을 위한 전체 새로고침 기능
        """
        # Given - 일부 데이터가 캐시된 상태
        mock_repository.exists_return_value = True
        mock_repository.read_json_return_value = {'initial': 'data'}
        data_loader.load_items()
        assert data_loader.is_cached('items.json'), (
            '초기 데이터가 캐시되어야 함'
        )

        # Given - 새로운 데이터로 변경
        mock_repository.read_json_return_value = {'reloaded': 'data'}
        mock_repository.read_json_calls.clear()

        # When - 전체 리로딩
        data_loader.reload_all()

        # Then - 모든 파일이 리로딩되었는지 확인
        expected_files = [
            'items.json',
            'enemies.json',
            'bosses.json',
            'game_balance.json',
        ]
        loaded_files = [str(call) for call in mock_repository.read_json_calls]

        for expected_file in expected_files:
            assert any(
                expected_file in loaded_file for loaded_file in loaded_files
            ), f'{expected_file}이 리로딩되어야 함'

        # Then - 새로운 데이터가 캐시에 저장되었는지 확인
        current_data = data_loader.load_items()
        assert current_data == {'reloaded': 'data'}, (
            '새로운 데이터가 로딩되어야 함'
        )

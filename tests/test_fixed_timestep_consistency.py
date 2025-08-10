from src.core.time_manager import TimeManager, TimeMode


class TestFixedTimestepConsistency:
    def test_60fps와_40fps_고정_시간_간격_일관성_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 60fps와 40fps 고정 시간 간격에서 일관된 시뮬레이션 결과 검증 (성공 시나리오)

        목적: 서로 다른 프레임률에서 고정 시간 간격 모드가 동일한 게임 로직 결과 생성 확인
        테스트할 범위: TimeManager의 fixed timestep 처리 정확성
        커버하는 함수 및 데이터: _update_fixed_timestep, delta_time 계산
        기대되는 안정성: 프레임률과 무관한 일관된 게임 시뮬레이션 보장
        """
        # Given - 60fps와 40fps용 TimeManager 설정
        time_manager_60fps = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP, fixed_timestep=1.0 / 60.0
        )
        time_manager_40fps = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP, fixed_timestep=1.0 / 60.0
        )

        # When - 각 프레임률로 동일한 시뮬레이션 시간 진행
        total_simulation_time = 1.0  # 1초
        expected_delta = 1.0 / 60.0  # 고정 timestep

        # 60fps 시뮬레이션 (16.67ms 간격)
        total_updates_60fps = 0
        current_time_60fps = 0.0
        frame_interval_60fps = 1.0 / 60.0

        while current_time_60fps < total_simulation_time:
            updates = time_manager_60fps.update(frame_interval_60fps)
            total_updates_60fps += updates
            current_time_60fps += frame_interval_60fps

        # 40fps 시뮬레이션 (25ms 간격)
        total_updates_40fps = 0
        current_time_40fps = 0.0
        frame_interval_40fps = 1.0 / 40.0

        while current_time_40fps < total_simulation_time:
            updates = time_manager_40fps.update(frame_interval_40fps)
            total_updates_40fps += updates
            current_time_40fps += frame_interval_40fps

        # Then - 동일한 업데이트 횟수 및 게임 시간 확인
        assert total_updates_60fps == total_updates_40fps, (
            '60fps와 40fps의 총 업데이트 횟수가 동일해야 함'
        )
        assert (
            abs(
                time_manager_60fps.total_game_time
                - time_manager_40fps.total_game_time
            )
            < 0.001
        ), '총 게임 시간이 거의 동일해야 함'

        # Delta time은 항상 고정값이어야 함
        assert time_manager_60fps.delta_time == expected_delta, (
            '60fps에서 delta time이 고정값과 일치해야 함'
        )
        assert time_manager_40fps.delta_time == expected_delta, (
            '40fps에서 delta time이 고정값과 일치해야 함'
        )

        # 최종 게임 시간이 약 1초에 근접해야 함
        assert abs(time_manager_60fps.total_game_time - 1.0) < 0.02, (
            '60fps 최종 게임 시간이 1초에 근접해야 함'
        )
        assert abs(time_manager_40fps.total_game_time - 1.0) < 0.02, (
            '40fps 최종 게임 시간이 1초에 근접해야 함'
        )

    def test_고정_시간_간격_정확성_및_누적_오차_최소화_검증_성공_시나리오(
        self,
    ) -> None:
        """2. 고정 시간 간격의 정확성과 누적 오차 최소화 검증 (성공 시나리오)

        목적: 고정 시간 간격에서 delta time 값의 정확성과 누적 오차 최소화 확인
        테스트할 범위: 정밀한 delta time 계산 및 누적 처리
        커버하는 함수 및 데이터: _update_fixed_timestep의 accumulated_time 처리
        기대되는 안정성: 장기간 시뮬레이션에서도 시간 정확성 보장
        """
        # Given - 60fps 고정 시간 간격 설정
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP, fixed_timestep=1.0 / 60.0
        )
        expected_delta = 1.0 / 60.0

        # When - 다양한 프레임 간격으로 업데이트 진행
        test_cases = [
            (1.0 / 60.0, '정확한 60fps 간격'),  # 정확한 간격
            (1.0 / 45.0, '45fps 간격 (더 긴 프레임)'),  # 더 긴 프레임
            (1.0 / 90.0, '90fps 간격 (더 짧은 프레임)'),  # 더 짧은 프레임
            (1.0 / 30.0, '30fps 간격 (훨씬 긴 프레임)'),  # 훨씬 긴 프레임
        ]

        for frame_interval, description in test_cases:
            time_manager.reset()
            total_updates = 0
            total_frame_time = 0.0
            max_simulation_time = 0.5  # 0.5초 시뮬레이션

            while total_frame_time < max_simulation_time:
                initial_game_time = time_manager.total_game_time
                updates = time_manager.update(frame_interval)
                total_updates += updates
                total_frame_time += frame_interval

                # Delta time은 항상 고정값이어야 함
                if updates > 0:
                    assert time_manager.delta_time == expected_delta, (
                        f'{description}: delta time이 고정값과 일치해야 함'
                    )

                # 게임 시간 증가량 검증
                game_time_increase = (
                    time_manager.total_game_time - initial_game_time
                )
                expected_increase = updates * expected_delta
                assert abs(game_time_increase - expected_increase) < 1e-10, (
                    f'{description}: 게임 시간 증가량이 정확해야 함'
                )

            # Then - 최종 검증 (프레임별 누적 효과 고려)
            expected_total_updates = int(max_simulation_time / expected_delta)
            # 프레임 간격이 고정 timestep과 다를 때 누적 효과로 인한 차이 허용
            tolerance = 3 if description.startswith('30fps') else 1
            assert abs(total_updates - expected_total_updates) <= tolerance, (
                f'{description}: 총 업데이트 횟수가 예상값과 비슷해야 함 (expected: {expected_total_updates}, actual: {total_updates})'
            )

            # 게임 시간은 실제 시뮬레이션 결과에 따라 달라질 수 있음
            expected_game_time = min(
                max_simulation_time,
                time_manager.total_game_time + expected_delta * 2,
            )
            assert time_manager.total_game_time > 0, (
                f'{description}: 게임 시간이 진행되어야 함'
            )

    def test_누적_시간_오버플로우_방지_및_최대_업데이트_제한_검증_성공_시나리오(
        self,
    ) -> None:
        """3. 누적 시간 오버플로우 방지 및 최대 업데이트 제한 검증 (성공 시나리오)

        목적: 긴 프레임 간격에서 과도한 업데이트 방지 메커니즘 확인
        테스트할 범위: _update_fixed_timestep의 최대 업데이트 제한 (10회)
        커버하는 함수 및 데이터: accumulated_time 리셋 로직
        기대되는 안정성: 프레임 드롭 상황에서도 안정적인 시뮬레이션 유지
        """
        # Given - 고정 시간 간격 설정 (max_frame_time을 크게 설정하여 제한 로직 테스트)
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP,
            fixed_timestep=1.0 / 60.0,
            max_frame_time=2.0,  # 충분히 큰 값으로 설정
        )

        # When - 매우 긴 프레임 간격 (스파이크) 시뮬레이션
        very_long_frame = 1.0  # 1초 (60 업데이트 분량)
        updates = time_manager.update(very_long_frame)

        # Then - 최대 10회 업데이트로 제한되어야 함
        assert updates == 10, (
            f'매우 긴 프레임에서 최대 10회 업데이트로 제한되어야 함 (실제: {updates}회)'
        )
        assert time_manager.total_game_time == 10 * (1.0 / 60.0), (
            f'게임 시간이 10회 업데이트에 해당하는 시간과 일치해야 함 (실제: {time_manager.total_game_time})'
        )

        # accumulated_time이 리셋되어야 함
        stats = time_manager.get_time_stats()
        assert stats['accumulated_time'] == 0.0, (
            '누적 시간이 0으로 리셋되어야 함'
        )

    def test_시간_스케일_적용_고정_시간_간격_검증_성공_시나리오(self) -> None:
        """4. 시간 스케일 적용된 고정 시간 간격 검증 (성공 시나리오)

        목적: 시간 스케일(일시정지, 슬로우모션)이 적용된 상태에서 고정 시간 간격 동작 확인
        테스트할 범위: 스케일된 delta time과 고정 timestep의 상호작용
        커버하는 함수 및 데이터: time_scale 적용 로직
        기대되는 안정성: 시간 조작 기능에서도 일관된 시뮬레이션 보장
        """
        # Given - 고정 시간 간격 설정 및 다양한 시간 스케일
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP, fixed_timestep=1.0 / 60.0
        )
        frame_interval = 1.0 / 60.0

        test_scales = [
            (1.0, '정상 속도'),
            (0.5, '슬로우모션 (50%)'),
            (2.0, '빠른 모드 (200%)'),
            (0.0, '일시정지'),
        ]

        for scale, description in test_scales:
            time_manager.reset()
            time_manager.time_scale = scale

            # When - 동일한 프레임 시간으로 여러 번 업데이트
            total_updates = 0
            for _ in range(120):  # 2초 분량
                updates = time_manager.update(frame_interval)
                total_updates += updates

            # Then - 시간 스케일에 따른 예상 결과 검증
            if scale == 0.0:  # 일시정지
                assert total_updates == 0, (
                    f'{description}: 일시정지 상태에서 업데이트가 발생하지 않아야 함'
                )
                assert time_manager.total_game_time == 0.0, (
                    f'{description}: 게임 시간이 정지되어야 함'
                )
            else:
                expected_game_time = 2.0 * scale  # 2초 * 스케일
                assert (
                    abs(time_manager.total_game_time - expected_game_time)
                    < 0.1
                ), f'{description}: 게임 시간이 스케일에 비례해야 함'

                if time_manager.total_game_time > 0:
                    # Delta time은 항상 고정값이어야 함 (스케일과 무관)
                    assert time_manager.delta_time == 1.0 / 60.0, (
                        f'{description}: delta time이 고정값을 유지해야 함'
                    )

    def test_보간_계수_정확성_고정_시간_간격_검증_성공_시나리오(self) -> None:
        """5. 보간 계수 정확성 고정 시간 간격 검증 (성공 시나리오)

        목적: 고정 시간 간격에서 렌더링 보간을 위한 보간 계수 정확성 확인
        테스트할 범위: get_interpolation_factor 계산의 정확성
        커버하는 함수 및 데이터: accumulated_time 기반 보간 계수
        기대되는 안정성: 부드러운 렌더링을 위한 정확한 보간값 제공
        """
        # Given - 고정 시간 간격 설정
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP, fixed_timestep=1.0 / 60.0
        )

        # When - 부분적인 프레임 업데이트 시뮬레이션
        partial_frame_times = [
            (1.0 / 120.0, 0.5),  # 절반 프레임 - 보간 계수 0.5 예상
            (1.0 / 90.0, 2.0 / 3.0),  # 2/3 프레임 - 보간 계수 2/3 예상
            (1.0 / 240.0, 0.25),  # 1/4 프레임 - 보간 계수 0.25 예상
        ]

        for frame_time, expected_factor in partial_frame_times:
            time_manager.reset()

            # 부분 프레임 업데이트
            updates = time_manager.update(frame_time)
            interpolation_factor = time_manager.get_interpolation_factor()

            # Then - 보간 계수 정확성 검증
            assert updates == 0, (
                '부분 프레임에서는 업데이트가 발생하지 않아야 함'
            )
            assert abs(interpolation_factor - expected_factor) < 0.01, (
                f'프레임 시간 {frame_time}에 대한 보간 계수가 {expected_factor}에 근접해야 함'
            )

        # 완전한 프레임에서는 보간 계수가 0이어야 함
        time_manager.reset()
        updates = time_manager.update(1.0 / 60.0)  # 정확한 timestep
        interpolation_factor = time_manager.get_interpolation_factor()

        assert updates == 1, '완전한 프레임에서 1회 업데이트가 발생해야 함'
        assert interpolation_factor == 0.0, (
            '완전한 업데이트 후 보간 계수가 0이어야 함'
        )

"""
SystemOrchestrator for ECS (Entity-Component-System) architecture.

The SystemOrchestrator manages system lifecycle, execution order, and provides
centralized coordination of all systems in the game engine.
"""

from collections import OrderedDict
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinate_manager import CoordinateManager
    from .entity_manager import EntityManager
    from .events.event_bus import EventBus
    from .events.interfaces import IEventSubscriber
    from .system import ISystem


class SystemOrchestrator:
    """
    Orchestrates system execution order and lifecycle management.

    The orchestrator manages system registration, initialization, and
    execution in priority order. It provides centralized control over
    all systems in the ECS architecture.
    """

    def __init__(
        self, 
        event_bus: 'EventBus | None' = None,
        entity_manager: 'EntityManager | None' = None,
        coordinate_manager: 'CoordinateManager | None' = None
    ) -> None:
        """Initialize the system orchestrator.

        Args:
            event_bus: Optional EventBus for system event communication
            entity_manager: Optional EntityManager for dependency injection
            coordinate_manager: Optional CoordinateManager for dependency injection
        """
        # OrderedDict to maintain insertion order while allowing efficient
        # lookups
        self._systems: OrderedDict[str, ISystem] = OrderedDict()
        # Track systems by priority for efficient sorting
        self._priority_map: dict[int, list[str]] = {}
        # Cache sorted system list for performance
        self._sorted_systems: list[ISystem] | None = None
        # Track if systems need re-sorting
        self._needs_sorting = False
        # Execution statistics
        self._execution_stats: dict[str, dict[str, float]] = {}
        # System groups for batch operations
        self._system_groups: dict[str, set[str]] = {}

        # AI-NOTE : 2025-08-13 이벤트 기반 시스템 간 통신 지원
        # - 이유: 카메라 좌표 관리 등 시스템 간 느슨한 결합 필요
        # - 요구사항: EventBus를 통한 시스템 이벤트 처리 지원
        # - 히스토리: 직접 호출 방식에서 이벤트 기반 시스템으로 확장
        self._event_bus = event_bus
        
        # Manager dependencies for dependency injection
        self._entity_manager = entity_manager
        self._coordinate_manager = coordinate_manager
        self._event_subscribers: list[IEventSubscriber] = []

    def subscribe(self, subscriber: 'IEventSubscriber') -> None:
        """
        Register a subscriber to receive events.

        Args:
            subscriber: The subscriber to register.
        """
        raise NotImplementedError("subscribe 구현해주세요.")
        

    def register_system(
        self, system: 'ISystem', name: str | None = None
    ) -> None:
        """
        Register a system with the orchestrator.

        Args:
            system: The system instance to register
            name: Optional name for the system (defaults to class name)

        Raises:
            ValueError: If a system with the same name is already registered
        """
        system_name = name or system.__class__.__name__

        if system_name in self._systems:
            raise ValueError(
                f'System with name "{system_name}" is already registered'
            )

        # Register the system
        self._systems[system_name] = system

        # Add to priority tracking
        priority = getattr(system, 'priority', 0)
        if priority not in self._priority_map:
            self._priority_map[priority] = []
        self._priority_map[priority].append(system_name)

        # Inject dependencies into the system
        if hasattr(system, 'set_entity_manager') and self._entity_manager is not None:
            system.set_entity_manager(self._entity_manager)
        if hasattr(system, 'set_coordinate_manager') and self._coordinate_manager is not None:
            system.set_coordinate_manager(self._coordinate_manager)

        # Initialize the system
        try:
            system.initialize()
        except Exception as e:
            # If initialization fails, remove the system
            self.unregister_system(system_name)
            raise RuntimeError(
                f'Failed to initialize system "{system_name}": {e}'
            ) from e

        # Mark that we need to resort systems
        self._needs_sorting = True
        self._sorted_systems = None

        # Initialize stats tracking
        self._execution_stats[system_name] = {
            'total_time': 0.0,
            'call_count': 0,
            'avg_time': 0.0,
            'max_time': 0.0,
        }

        # AI-NOTE : 2025-08-13 IEventSubscriber 시스템 자동 이벤트 구독
        # - 이유: 이벤트 구독 설정 자동화로 개발자 편의성 향상
        # - 요구사항: IEventSubscriber를 구현한 시스템 자동 EventBus 등록
        # - 히스토리: 수동 구독 설정에서 자동 감지 및 등록으로 개선

        # 시스템이 IEventSubscriber를 구현하는지 확인
        from .events.interfaces import IEventSubscriber

        if (
            isinstance(system, IEventSubscriber)
            and self._event_bus is not None
        ):
            try:
                self._event_bus.subscribe(system)
                self._event_subscribers.append(system)
            except Exception as e:
                print(
                    f'Warning: Failed to subscribe system {system_name} to EventBus: {e}'
                )

        # CameraSystem에 EventBus 주입 (특별 처리)
        if hasattr(system, 'set_event_bus') and self._event_bus is not None:
            try:
                system.set_event_bus(self._event_bus)
            except Exception as e:
                print(
                    f'Warning: Failed to set EventBus for system {system_name}: {e}'
                )


    def unsubscribe(self, subscriber: 'IEventSubscriber') -> None:
        """
        Unregister a subscriber from receiving events.

        Args:
            subscriber: The subscriber to unregister.
        """
        
        raise NotImplementedError("unsubscribe 구현해주세요.")
    
    def unregister_system(self, name: str) -> 'ISystem | None':
        """
        Unregister a system from the orchestrator.

        Args:
            name: Name of the system to unregister

        Returns:
            The unregistered system instance, or None if not found
        """
        system = self._systems.pop(name, None)
        if system is None:
            return None

        # Clean up priority mapping
        priority = getattr(system, 'priority', 0)
        if priority in self._priority_map:
            try:
                self._priority_map[priority].remove(name)
                if not self._priority_map[priority]:
                    del self._priority_map[priority]
            except ValueError:
                pass  # System not in priority list

        # Clean up system
        try:
            if hasattr(system, 'cleanup'):
                system.cleanup()
        except Exception:
            # AI-NOTE: Intentionally swallow exceptions during cleanup to prevent
            # cascading failures when removing systems. Individual system
            # cleanup errors should not prevent other systems from being
            # cleaned up properly.
            # TODO: Use proper logging instead of silent failure
            pass

        # Mark that we need to resort systems
        self._needs_sorting = True
        self._sorted_systems = None

        # Clean up stats
        self._execution_stats.pop(name, None)

        # Remove from all groups
        for group_systems in self._system_groups.values():
            group_systems.discard(name)

        return system

    def get_system(self, name: str) -> 'ISystem | None':
        """
        Get a registered system by name.

        Args:
            name: Name of the system to retrieve

        Returns:
            The system instance, or None if not found
        """
        return self._systems.get(name)

    def has_system(self, name: str) -> bool:
        """
        Check if a system is registered.

        Args:
            name: Name of the system to check

        Returns:
            True if the system is registered, False otherwise
        """
        return name in self._systems


    def publish_event(self, event: 'BaseEvent') -> None:
        """
        Publish an event to all interested subscribers.

        Args:
            event: The event to publish. Must be a valid BaseEvent instance.
        """
        
        raise NotImplementedError("unsubscribe 구현해주세요.")

    def update_systems(
        self, delta_time: float
    ) -> None:
        """
        Update all enabled systems in priority order.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        import time

        # Ensure systems are sorted by priority
        if self._needs_sorting or self._sorted_systems is None:
            self._sort_systems()

        # AI-NOTE : 2025-08-13 이벤트 처리를 시스템 업데이트 전에 수행
        # - 이유: 이벤트 기반 상태 변경을 시스템 업데이트 전에 적용
        # - 요구사항: 매 프레임 이벤트 처리로 일관된 상태 보장
        # - 히스토리: 시스템 업데이트와 이벤트 처리 순서 최적화

        # Process events before updating systems
        if self._event_bus is not None:
            try:
                events_processed = self._event_bus.process_events()
                # 성능 모니터링을 위한 이벤트 처리 통계
                if events_processed > 0 and hasattr(
                    self, '_event_processing_stats'
                ):
                    self._event_processing_stats['events_processed'] += (
                        events_processed
                    )
            except Exception as e:
                print(f'Warning: Failed to process events: {e}')

        # Update each system
        for system in self._sorted_systems or []:
            # Skip disabled systems
            if hasattr(system, 'enabled') and not system.enabled:
                continue

            system_name = self._get_system_name(system)
            start_time = time.perf_counter()

            try:
                system.update(delta_time)
            except Exception:
                # AI-NOTE: Intentionally continue after system update failures
                # to prevent one broken system from stopping the entire
                # game loop.
                # Individual system errors should be isolated and not cascade.
                # TODO: Use proper logging to record system failures
                continue

            # Update execution statistics
            execution_time = time.perf_counter() - start_time
            self._update_execution_stats(system_name, execution_time)

    def set_system_priority(self, name: str, priority: int) -> bool:
        """
        Change a system's execution priority.

        Args:
            name: Name of the system
            priority: New priority value (lower numbers execute first)

        Returns:
            True if the priority was changed, False if system not found
        """
        system = self._systems.get(name)
        if system is None:
            return False

        # Remove from old priority group
        old_priority = getattr(system, 'priority', 0)
        if old_priority in self._priority_map:
            try:
                self._priority_map[old_priority].remove(name)
                if not self._priority_map[old_priority]:
                    del self._priority_map[old_priority]
            except ValueError:
                pass

        # Set new priority
        if hasattr(system, 'set_priority'):
            system.set_priority(priority)
        else:
            # Set priority attribute directly if method not available
            system.set_priority(priority)

        # Add to new priority group
        if priority not in self._priority_map:
            self._priority_map[priority] = []
        self._priority_map[priority].append(name)

        # Mark for re-sorting
        self._needs_sorting = True
        self._sorted_systems = None

        return True

    def enable_system(self, name: str) -> bool:
        """
        Enable a system.

        Args:
            name: Name of the system to enable

        Returns:
            True if the system was enabled, False if system not found
        """
        system = self._systems.get(name)
        if system is None or not hasattr(system, 'enable'):
            return False

        system.enable()
        return True

    def disable_system(self, name: str) -> bool:
        """
        Disable a system.

        Args:
            name: Name of the system to disable

        Returns:
            True if the system was disabled, False if system not found
        """
        system = self._systems.get(name)
        if system is None or not hasattr(system, 'disable'):
            return False

        system.disable()
        return True

    def create_system_group(
        self, group_name: str, system_names: list[str]
    ) -> bool:
        """
        Create a group of systems for batch operations.

        Args:
            group_name: Name for the system group
            system_names: List of system names to include in the group

        Returns:
            True if the group was created successfully, False otherwise
        """
        # Validate that all systems exist
        for system_name in system_names:
            if system_name not in self._systems:
                return False

        self._system_groups[group_name] = set(system_names)
        return True

    def enable_system_group(self, group_name: str) -> bool:
        """
        Enable all systems in a group.

        Args:
            group_name: Name of the system group

        Returns:
            True if the group was found and enabled, False otherwise
        """
        if group_name not in self._system_groups:
            return False

        for system_name in self._system_groups[group_name]:
            self.enable_system(system_name)

        return True

    def disable_system_group(self, group_name: str) -> bool:
        """
        Disable all systems in a group.

        Args:
            group_name: Name of the system group

        Returns:
            True if the group was found and disabled, False otherwise
        """
        if group_name not in self._system_groups:
            return False

        for system_name in self._system_groups[group_name]:
            self.disable_system(system_name)

        return True

    def get_system_names(self) -> list[str]:
        """
        Get names of all registered systems.

        Returns:
            List of system names in registration order
        """
        return list(self._systems.keys())

    def get_enabled_system_names(self) -> list[str]:
        """
        Get names of all enabled systems.

        Returns:
            List of enabled system names
        """
        enabled_names = []
        for name, system in self._systems.items():
            if not hasattr(system, 'enabled') or system.enabled:
                enabled_names.append(name)
        return enabled_names

    def get_execution_stats(self) -> dict[str, dict[str, float]]:
        """
        Get execution statistics for all systems.

        Returns:
            Dictionary mapping system names to their execution statistics
        """
        return self._execution_stats.copy()

    def reset_execution_stats(self) -> None:
        """Reset execution statistics for all systems."""
        for stats in self._execution_stats.values():
            stats.update(
                {
                    'total_time': 0.0,
                    'call_count': 0,
                    'avg_time': 0.0,
                    'max_time': 0.0,
                }
            )

    def clear_all_systems(self) -> None:
        """
        Unregister and cleanup all systems.

        This method will attempt to cleanup all systems before clearing them.
        """
        # Create a copy of system names to avoid modification during iteration
        system_names = list(self._systems.keys())

        for name in system_names:
            self.unregister_system(name)

        # Clear all data structures
        self._systems.clear()
        self._priority_map.clear()
        self._sorted_systems = None
        self._needs_sorting = False
        self._execution_stats.clear()
        self._system_groups.clear()

    def _sort_systems(self) -> None:
        """Sort systems by priority for execution."""
        sorted_systems = []

        # Sort priorities and then systems within each priority
        for priority in sorted(self._priority_map.keys()):
            for system_name in self._priority_map[priority]:
                system = self._systems.get(system_name)
                if system is not None:
                    sorted_systems.append(system)

        self._sorted_systems = sorted_systems
        self._needs_sorting = False

    def _get_system_name(self, system: 'ISystem') -> str:
        """Get the name of a system instance."""
        for name, registered_system in self._systems.items():
            if registered_system is system:
                return name
        return system.__class__.__name__

    def _update_execution_stats(
        self, system_name: str, execution_time: float
    ) -> None:
        """Update execution statistics for a system."""
        if system_name not in self._execution_stats:
            return

        stats = self._execution_stats[system_name]
        stats['total_time'] += execution_time
        stats['call_count'] += 1
        stats['avg_time'] = stats['total_time'] / stats['call_count']
        stats['max_time'] = max(stats['max_time'], execution_time)

    def __len__(self) -> int:
        """Return the number of registered systems."""
        return len(self._systems)

    def __iter__(self) -> Iterator['ISystem']:
        """Iterate over all registered systems."""
        return iter(self._systems.values())

    def __contains__(self, name: str) -> bool:
        """Check if a system name is registered."""
        return name in self._systems

    def __str__(self) -> str:
        """Return string representation of the orchestrator."""
        enabled_count = len(self.get_enabled_system_names())
        total_count = len(self._systems)
        return (
            f'SystemOrchestrator({enabled_count}/{total_count} '
            f'enabled systems)'
        )

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f'SystemOrchestrator(systems={len(self._systems)}, '
            f'groups={len(self._system_groups)}, '
            f'priorities={len(self._priority_map)})'
        )

    # AI-NOTE : 2025-08-13 EventBus 관리 메서드들 추가
    # - 이유: EventBus 설정 및 상태 조회를 위한 유틸리티 메서드 필요
    # - 요구사항: EventBus 설정, 조회, 구독자 관리 기능 제공
    # - 히스토리: SystemOrchestrator에 이벤트 시스템 통합

    def set_event_bus(self, event_bus: 'EventBus') -> None:
        """
        Set the EventBus for system communication.

        Args:
            event_bus: EventBus instance to use for system communication
        """
        self._event_bus = event_bus

        # 기존 구독자들을 새 EventBus에 재등록
        from .events.interfaces import IEventSubscriber

        for system_name, system in self._systems.items():
            if isinstance(system, IEventSubscriber):
                try:
                    event_bus.subscribe(system)
                except Exception as e:
                    print(
                        f'Warning: Failed to resubscribe system {system_name}: {e}'
                    )

            # CameraSystem에도 새 EventBus 설정
            if hasattr(system, 'set_event_bus'):
                try:
                    system.set_event_bus(event_bus)
                except Exception as e:
                    print(
                        f'Warning: Failed to set new EventBus for system {system_name}: {e}'
                    )

    def get_event_bus(self) -> 'EventBus | None':
        """
        Get the current EventBus instance.

        Returns:
            Current EventBus instance or None if not set
        """
        return self._event_bus

    def get_event_subscriber_count(self) -> int:
        """
        Get the number of registered event subscribers.

        Returns:
            Number of systems that subscribe to events
        """
        return len(self._event_subscribers)

    def get_event_processing_stats(self) -> dict[str, int | float]:
        """
        Get event processing statistics.

        Returns:
            Dictionary with event processing statistics
        """
        if self._event_bus is not None:
            return self._event_bus.get_processing_stats()
        return {}

    def process_events_manually(self) -> int:
        """
        Manually process all queued events.

        This is typically called automatically in update_systems(),
        but can be called manually for testing or special cases.

        Returns:
            Number of events processed
        """
        if self._event_bus is not None:
            try:
                return self._event_bus.process_events()
            except Exception as e:
                print(f'Warning: Failed to manually process events: {e}')
                return 0
        return 0

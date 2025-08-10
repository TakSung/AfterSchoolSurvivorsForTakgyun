"""
SystemOrchestrator for ECS (Entity-Component-System) architecture.

The SystemOrchestrator manages system lifecycle, execution order, and provides
centralized coordination of all systems in the game engine.
"""

from collections import OrderedDict
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entity_manager import EntityManager
    from .system import ISystem


class SystemOrchestrator:
    """
    Orchestrates system execution order and lifecycle management.

    The orchestrator manages system registration, initialization, and
    execution in priority order. It provides centralized control over
    all systems in the ECS architecture.
    """

    def __init__(self) -> None:
        """Initialize the system orchestrator."""
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

    def update_systems(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update all enabled systems in priority order.

        Args:
            entity_manager: The entity manager to pass to systems
            delta_time: Time elapsed since last update in seconds
        """
        import time

        # Ensure systems are sorted by priority
        if self._needs_sorting or self._sorted_systems is None:
            self._sort_systems()

        # Update each system
        for system in self._sorted_systems or []:
            # Skip disabled systems
            if hasattr(system, 'enabled') and not system.enabled:
                continue

            system_name = self._get_system_name(system)
            start_time = time.perf_counter()

            try:
                system.update(entity_manager, delta_time)
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
            system._priority = priority  # type: ignore

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

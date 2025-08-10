"""
Tests for core ECS classes: Entity, Component, and System.
"""

import pytest
from dataclasses import dataclass
from typing import Any

from src.core.entity import Entity
from src.core.component import Component
from src.core.system import System, ISystem


# Test component implementations for testing
@dataclass
class TestComponent(Component):
    """Test component with simple data."""
    value: int
    name: str = "test"


@dataclass
class AnotherComponent(Component):
    """Another test component."""
    x: float
    y: float


# Test system implementation for testing
class TestSystem(System):
    """Test system implementation."""
    
    def __init__(self) -> None:
        super().__init__(priority=1)
        self.update_count = 0
    
    def update(self, entity_manager: Any, delta_time: float) -> None:
        """Test update method."""
        self.update_count += 1
    
    def get_required_components(self) -> list[type]:
        """Return required components for this system."""
        return [TestComponent]


class TestEntity:
    """Test cases for Entity class."""
    
    def test_entity_creation(self) -> None:
        """Test entity creation with unique IDs."""
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        assert entity1.entity_id != entity2.entity_id
        assert entity1.active is True
        assert entity2.active is True
    
    def test_entity_lifecycle(self) -> None:
        """Test entity activation/deactivation."""
        entity = Entity.create()
        
        assert entity.active is True
        
        entity.deactivate()
        assert entity.active is False
        
        entity.activate()
        assert entity.active is True
        
        entity.destroy()
        assert entity.active is False
    
    def test_entity_equality(self) -> None:
        """Test entity equality based on ID."""
        entity1 = Entity.create()
        entity2 = Entity.create()
        entity3 = Entity(entity_id=entity1.entity_id)
        
        assert entity1 == entity3  # Same ID
        assert entity1 != entity2  # Different IDs
        assert entity1 != "not_an_entity"  # Different type
    
    def test_entity_hashable(self) -> None:
        """Test that entities can be used in sets and as dict keys."""
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        entity_set = {entity1, entity2, entity1}
        assert len(entity_set) == 2
        
        entity_dict = {entity1: "value1", entity2: "value2"}
        assert entity_dict[entity1] == "value1"


class TestComponent:
    """Test cases for Component base class."""
    
    def test_component_creation(self) -> None:
        """Test component creation with dataclass."""
        component = TestComponent(value=42, name="test_comp")
        
        assert component.value == 42
        assert component.name == "test_comp"
    
    def test_component_validation(self) -> None:
        """Test component validation."""
        component = TestComponent(value=10)
        assert component.validate() is True
    
    def test_component_copy(self) -> None:
        """Test component copying."""
        original = TestComponent(value=100, name="original")
        copy = original.copy()
        
        assert copy is not original
        assert copy.value == original.value
        assert copy.name == original.name
    
    def test_component_serialization(self) -> None:
        """Test component serialization and deserialization."""
        component = TestComponent(value=50, name="serialized")
        
        data = component.serialize()
        assert data == {"value": 50, "name": "serialized"}
        
        restored = TestComponent.deserialize(data)
        assert restored.value == component.value
        assert restored.name == component.name


class TestSystem:
    """Test cases for System base class."""
    
    def test_system_creation(self) -> None:
        """Test system creation with default values."""
        system = TestSystem()
        
        assert system.priority == 1
        assert system.enabled is True
        assert system.initialized is False
    
    def test_system_state_management(self) -> None:
        """Test system enable/disable and initialization."""
        system = TestSystem()
        
        system.disable()
        assert system.enabled is False
        
        system.enable()
        assert system.enabled is True
        
        system.initialize()
        assert system.initialized is True
    
    def test_system_priority(self) -> None:
        """Test system priority setting."""
        system = TestSystem()
        
        assert system.priority == 1
        
        system.set_priority(5)
        assert system.priority == 5
    
    def test_system_required_components(self) -> None:
        """Test system required components."""
        system = TestSystem()
        required = system.get_required_components()
        
        assert required == [TestComponent]
    
    def test_system_update(self) -> None:
        """Test system update method."""
        system = TestSystem()
        
        assert system.update_count == 0
        
        system.update(None, 0.016)
        assert system.update_count == 1
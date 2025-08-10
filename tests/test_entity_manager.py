"""
Tests for EntityManager class in the ECS architecture.
"""

import pytest
from dataclasses import dataclass

from src.core.entity import Entity
from src.core.component import Component
from src.core.entity_manager import EntityManager


# Test components for testing purposes
@dataclass
class TestPositionComponent(Component):
    """Test position component."""
    x: float = 0.0
    y: float = 0.0


@dataclass
class TestHealthComponent(Component):
    """Test health component."""
    current: int = 100
    maximum: int = 100


@dataclass
class TestVelocityComponent(Component):
    """Test velocity component."""
    dx: float = 0.0
    dy: float = 0.0


class TestEntityManager:
    """Test cases for EntityManager class."""
    
    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.entity_manager = EntityManager()
    
    def test_create_entity(self) -> None:
        """Test entity creation."""
        entity = self.entity_manager.create_entity()
        
        assert entity is not None
        assert entity.entity_id is not None
        assert entity.active is True
        assert entity in self.entity_manager
        assert len(self.entity_manager) == 1
    
    def test_create_multiple_entities(self) -> None:
        """Test creating multiple entities with unique IDs."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        assert entity1.entity_id != entity2.entity_id
        assert entity2.entity_id != entity3.entity_id
        assert entity1.entity_id != entity3.entity_id
        assert len(self.entity_manager) == 3
    
    def test_destroy_entity(self) -> None:
        """Test entity destruction."""
        entity = self.entity_manager.create_entity()
        entity_id = entity.entity_id
        
        assert entity in self.entity_manager
        assert len(self.entity_manager) == 1
        
        self.entity_manager.destroy_entity(entity)
        
        assert entity not in self.entity_manager
        assert len(self.entity_manager) == 0
        assert not entity.active
        assert self.entity_manager.get_entity(entity_id) is None
    
    def test_destroy_nonexistent_entity(self) -> None:
        """Test destroying an entity that doesn't exist."""
        entity = Entity.create()  # Create without adding to manager
        
        # Should not raise an error
        self.entity_manager.destroy_entity(entity)
        assert len(self.entity_manager) == 0
    
    def test_get_entity(self) -> None:
        """Test entity retrieval by ID."""
        entity = self.entity_manager.create_entity()
        
        retrieved = self.entity_manager.get_entity(entity.entity_id)
        assert retrieved is entity
        assert retrieved.entity_id == entity.entity_id
    
    def test_get_nonexistent_entity(self) -> None:
        """Test retrieving an entity that doesn't exist."""
        result = self.entity_manager.get_entity("nonexistent-id")
        assert result is None
    
    def test_get_all_entities(self) -> None:
        """Test getting all entities."""
        entities = []
        for _ in range(3):
            entities.append(self.entity_manager.create_entity())
        
        all_entities = self.entity_manager.get_all_entities()
        assert len(all_entities) == 3
        
        for entity in entities:
            assert entity in all_entities
    
    def test_get_active_entities(self) -> None:
        """Test getting only active entities."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        # Deactivate one entity
        entity2.deactivate()
        
        active_entities = self.entity_manager.get_active_entities()
        assert len(active_entities) == 2
        assert entity1 in active_entities
        assert entity2 not in active_entities
        assert entity3 in active_entities
    
    def test_add_component(self) -> None:
        """Test adding components to entities."""
        entity = self.entity_manager.create_entity()
        position = TestPositionComponent(x=10.0, y=20.0)
        
        self.entity_manager.add_component(entity, position)
        
        retrieved = self.entity_manager.get_component(entity, TestPositionComponent)
        assert retrieved is position
        assert retrieved.x == 10.0
        assert retrieved.y == 20.0
    
    def test_add_component_to_nonexistent_entity(self) -> None:
        """Test adding component to non-existent entity."""
        entity = Entity.create()  # Create without adding to manager
        position = TestPositionComponent()
        
        with pytest.raises(ValueError):
            self.entity_manager.add_component(entity, position)
    
    def test_remove_component(self) -> None:
        """Test removing components from entities."""
        entity = self.entity_manager.create_entity()
        position = TestPositionComponent(x=10.0, y=20.0)
        health = TestHealthComponent(current=50)
        
        self.entity_manager.add_component(entity, position)
        self.entity_manager.add_component(entity, health)
        
        assert self.entity_manager.has_component(entity, TestPositionComponent)
        assert self.entity_manager.has_component(entity, TestHealthComponent)
        
        self.entity_manager.remove_component(entity, TestPositionComponent)
        
        assert not self.entity_manager.has_component(entity, TestPositionComponent)
        assert self.entity_manager.has_component(entity, TestHealthComponent)
        assert self.entity_manager.get_component(entity, TestPositionComponent) is None
    
    def test_remove_component_from_nonexistent_entity(self) -> None:
        """Test removing component from non-existent entity."""
        entity = Entity.create()
        
        # Should not raise an error
        self.entity_manager.remove_component(entity, TestPositionComponent)
    
    def test_has_component(self) -> None:
        """Test checking if entity has component."""
        entity = self.entity_manager.create_entity()
        position = TestPositionComponent()
        
        assert not self.entity_manager.has_component(entity, TestPositionComponent)
        
        self.entity_manager.add_component(entity, position)
        
        assert self.entity_manager.has_component(entity, TestPositionComponent)
        assert not self.entity_manager.has_component(entity, TestHealthComponent)
    
    def test_get_entities_with_component(self) -> None:
        """Test getting entities with specific component."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        self.entity_manager.add_component(entity1, TestPositionComponent())
        self.entity_manager.add_component(entity2, TestPositionComponent())
        self.entity_manager.add_component(entity3, TestHealthComponent())
        
        position_entities = self.entity_manager.get_entities_with_component(TestPositionComponent)
        health_entities = self.entity_manager.get_entities_with_component(TestHealthComponent)
        
        assert len(position_entities) == 2
        assert entity1 in position_entities
        assert entity2 in position_entities
        assert entity3 not in position_entities
        
        assert len(health_entities) == 1
        assert entity3 in health_entities
    
    def test_get_entities_with_components_multiple(self) -> None:
        """Test getting entities with multiple components."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        self.entity_manager.add_component(entity1, TestPositionComponent())
        self.entity_manager.add_component(entity1, TestHealthComponent())
        
        self.entity_manager.add_component(entity2, TestPositionComponent())
        
        self.entity_manager.add_component(entity3, TestHealthComponent())
        self.entity_manager.add_component(entity3, TestVelocityComponent())
        
        # Entity with both Position and Health
        entities = self.entity_manager.get_entities_with_components(
            TestPositionComponent, TestHealthComponent
        )
        assert len(entities) == 1
        assert entity1 in entities
        
        # Entity with Health and Velocity
        entities = self.entity_manager.get_entities_with_components(
            TestHealthComponent, TestVelocityComponent
        )
        assert len(entities) == 1
        assert entity3 in entities
        
        # No entity has all three components
        entities = self.entity_manager.get_entities_with_components(
            TestPositionComponent, TestHealthComponent, TestVelocityComponent
        )
        assert len(entities) == 0
    
    def test_get_entities_with_no_component_types(self) -> None:
        """Test getting entities with no component type filters."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        
        entities = self.entity_manager.get_entities_with_components()
        assert len(entities) == 2
        assert entity1 in entities
        assert entity2 in entities
    
    def test_get_components_for_entity(self) -> None:
        """Test getting all components for a specific entity."""
        entity = self.entity_manager.create_entity()
        position = TestPositionComponent(x=5.0, y=10.0)
        health = TestHealthComponent(current=75)
        
        self.entity_manager.add_component(entity, position)
        self.entity_manager.add_component(entity, health)
        
        components = self.entity_manager.get_components_for_entity(entity)
        
        assert len(components) == 2
        assert TestPositionComponent in components
        assert TestHealthComponent in components
        assert components[TestPositionComponent] is position
        assert components[TestHealthComponent] is health
    
    def test_clear_all(self) -> None:
        """Test clearing all entities and components."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        
        self.entity_manager.add_component(entity1, TestPositionComponent())
        self.entity_manager.add_component(entity2, TestHealthComponent())
        
        assert len(self.entity_manager) == 2
        assert self.entity_manager.get_component_count(TestPositionComponent) == 1
        
        self.entity_manager.clear_all()
        
        assert len(self.entity_manager) == 0
        assert self.entity_manager.get_component_count(TestPositionComponent) == 0
        assert self.entity_manager.get_component_count(TestHealthComponent) == 0
        assert not entity1.active
        assert not entity2.active
    
    def test_entity_count_methods(self) -> None:
        """Test entity counting methods."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        assert self.entity_manager.get_entity_count() == 3
        assert self.entity_manager.get_active_entity_count() == 3
        
        entity2.deactivate()
        
        assert self.entity_manager.get_entity_count() == 3
        assert self.entity_manager.get_active_entity_count() == 2
        
        self.entity_manager.destroy_entity(entity3)
        
        assert self.entity_manager.get_entity_count() == 2
        assert self.entity_manager.get_active_entity_count() == 1
    
    def test_component_count(self) -> None:
        """Test component counting."""
        entity1 = self.entity_manager.create_entity()
        entity2 = self.entity_manager.create_entity()
        entity3 = self.entity_manager.create_entity()
        
        self.entity_manager.add_component(entity1, TestPositionComponent())
        self.entity_manager.add_component(entity2, TestPositionComponent())
        self.entity_manager.add_component(entity3, TestHealthComponent())
        
        assert self.entity_manager.get_component_count(TestPositionComponent) == 2
        assert self.entity_manager.get_component_count(TestHealthComponent) == 1
        assert self.entity_manager.get_component_count(TestVelocityComponent) == 0
    
    def test_destroy_entity_removes_components(self) -> None:
        """Test that destroying an entity removes all its components."""
        entity = self.entity_manager.create_entity()
        
        self.entity_manager.add_component(entity, TestPositionComponent())
        self.entity_manager.add_component(entity, TestHealthComponent())
        self.entity_manager.add_component(entity, TestVelocityComponent())
        
        assert self.entity_manager.get_component_count(TestPositionComponent) == 1
        assert self.entity_manager.get_component_count(TestHealthComponent) == 1
        assert self.entity_manager.get_component_count(TestVelocityComponent) == 1
        
        self.entity_manager.destroy_entity(entity)
        
        assert self.entity_manager.get_component_count(TestPositionComponent) == 0
        assert self.entity_manager.get_component_count(TestHealthComponent) == 0
        assert self.entity_manager.get_component_count(TestVelocityComponent) == 0
    
    def test_iterator_protocol(self) -> None:
        """Test EntityManager iterator protocol."""
        entities = []
        for _ in range(3):
            entities.append(self.entity_manager.create_entity())
        
        # Test __iter__
        iterated_entities = []
        for entity in self.entity_manager:
            iterated_entities.append(entity)
        
        assert len(iterated_entities) == 3
        for entity in entities:
            assert entity in iterated_entities
    
    def test_contains_protocol(self) -> None:
        """Test EntityManager __contains__ method."""
        entity1 = self.entity_manager.create_entity()
        entity2 = Entity.create()  # Not added to manager
        
        assert entity1 in self.entity_manager
        assert entity2 not in self.entity_manager
        
        self.entity_manager.destroy_entity(entity1)
        assert entity1 not in self.entity_manager
    
    def test_string_representations(self) -> None:
        """Test string representation methods."""
        assert "EntityManager" in str(self.entity_manager)
        assert "EntityManager" in repr(self.entity_manager)
        
        entity = self.entity_manager.create_entity()
        entity_str = str(self.entity_manager)
        entity_repr = repr(self.entity_manager)
        
        assert "1" in entity_str  # Should show 1 active entity
        assert "entities=1" in entity_repr
        assert "active=1" in entity_repr
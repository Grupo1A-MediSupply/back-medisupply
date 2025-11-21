"""
Tests unitarios para Shared Entity
"""
import pytest
from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId


@pytest.mark.unit
class TestEntity:
    """Tests para Entity base"""
    
    def test_entity_creation(self):
        """Test crear entidad"""
        class TestEntity(Entity):
            pass
        
        entity_id = EntityId("test-id")
        entity = TestEntity(entity_id)
        
        assert entity.id == entity_id
    
    def test_entity_equality(self):
        """Test igualdad de entidades"""
        class TestEntity(Entity):
            pass
        
        entity_id = EntityId("test-id")
        entity1 = TestEntity(entity_id)
        entity2 = TestEntity(entity_id)
        
        assert entity1 == entity2
    
    def test_entity_hash(self):
        """Test hash de entidad"""
        class TestEntity(Entity):
            pass
        
        entity_id = EntityId("test-id")
        entity = TestEntity(entity_id)
        
        assert hash(entity) == hash(entity_id)


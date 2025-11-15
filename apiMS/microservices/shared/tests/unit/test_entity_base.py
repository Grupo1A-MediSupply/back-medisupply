"""
Tests unitarios para la clase base Entity y eventos de dominio
"""
import pytest

# Los paths están configurados en conftest.py
# Los imports se hacen dentro de las funciones para evitar problemas cuando pytest carga el módulo


def test_entity_records_and_clears_domain_events():
    from domain.entity import Entity
    from domain.events import DomainEvent
    from domain.value_objects import EntityId
    
    class DummyCreatedEvent(DomainEvent):
        def __init__(self, data: str):
            super().__init__()
            self.data = data

        def _event_data(self):
            return {"data": self.data}

    class DummyEntity(Entity):
        def __init__(self, entity_id: EntityId):
            super().__init__(entity_id)

        def create_something(self, payload: str):
            self._record_event(DummyCreatedEvent(payload))
    
    de = DummyEntity(EntityId("e1"))
    assert de.get_domain_events() == []

    de.create_something("hello")
    events = de.get_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], DummyCreatedEvent)
    assert events[0].to_dict()["data"]["data"] == "hello"
    assert events[0].aggregate_id == "e1"

    de.clear_domain_events()
    assert de.get_domain_events() == []


def test_entity_equality_and_hash():
    from domain.entity import Entity
    from domain.value_objects import EntityId
    
    class DummyEntity(Entity):
        def __init__(self, entity_id: EntityId):
            super().__init__(entity_id)
    
    a = DummyEntity(EntityId("x"))
    b = DummyEntity(EntityId("x"))
    c = DummyEntity(EntityId("y"))

    assert a == b
    assert a != c
    assert len({a, b, c}) == 2



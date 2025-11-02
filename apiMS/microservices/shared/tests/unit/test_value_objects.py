"""
Tests unitarios para Value Objects compartidos: Email, EntityId, Money
"""
import pytest

# Los paths están configurados en conftest.py
# Los imports se hacen dentro de las funciones para evitar problemas cuando pytest carga el módulo


def test_email_valid_and_invalid():
    from domain.value_objects import Email
    assert str(Email("user@example.com")) == "user@example.com"

    with pytest.raises(ValueError):
        Email("invalid-email")


def test_entity_id_valid_and_invalid_and_equality():
    from domain.value_objects import EntityId
    eid1 = EntityId("abc")
    eid2 = EntityId("abc")
    eid3 = EntityId("xyz")

    assert str(eid1) == "abc"
    assert eid1 == eid2
    assert eid1 != eid3

    with pytest.raises(ValueError):
        EntityId("")


def test_money_basic_operations_and_validation():
    from domain.value_objects import Money
    m1 = Money(10.0, "USD")
    m2 = Money(5.25, "USD")
    m3 = m1 + m2
    assert str(m3) == "15.25 USD"

    m4 = m1 - m2
    assert str(m4) == "4.75 USD"

    with pytest.raises(ValueError):
        Money(-1.0, "USD")

    with pytest.raises(ValueError):
        Money(1.0, "US")

    with pytest.raises(ValueError):
        _ = Money(1.0, "USD") + Money(1.0, "EUR")

    with pytest.raises(ValueError):
        _ = Money(1.0, "USD") - Money(1.0, "EUR")



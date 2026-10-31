import copy

import pytest

from models.exceptions import ValidationError
from models.history import CREATED_FIELD, HistoryEntry, build_entries
from models.ticket import Ticket


def test_no_changes_no_entries():
    t = Ticket(title="x")
    assert build_entries(copy.deepcopy(t), t, changed_by="u1") == []


def test_detects_each_changed_field():
    old = Ticket(title="x", priority="baja")
    new = copy.deepcopy(old)
    new.change_status("en_progreso")
    new.change_priority("alta")
    new.assign("u2")
    new.add_label("backend")

    entries = {e.field_name: e for e in build_entries(old, new, changed_by="u1")}
    assert set(entries) == {"status", "priority", "assignee_id", "labels"}
    assert entries["status"].old_value == "nuevo"
    assert entries["status"].new_value == "en_progreso"
    assert entries["priority"].old_value == "baja"
    assert entries["assignee_id"].old_value is None
    assert entries["assignee_id"].new_value == "u2"
    assert entries["labels"].new_value == "backend"
    assert all(e.changed_by == "u1" and e.ticket_id == old.id for e in entries.values())


def test_same_object_gives_no_entries():
    t = Ticket(title="x")
    t.change_status("hecho")
    assert build_entries(t, t) == []  # advertido en la documentación


def test_different_tickets_rejected():
    with pytest.raises(ValidationError):
        build_entries(Ticket(title="a"), Ticket(title="b"))


def test_creation_entry():
    t = Ticket(title="Nuevo")
    e = HistoryEntry.for_creation(t, changed_by="u1")
    assert e.field_name == CREATED_FIELD
    assert e.new_value == "Nuevo" and e.old_value is None


def test_entry_validation_and_roundtrip():
    with pytest.raises(ValidationError):
        HistoryEntry(ticket_id="", field_name="status")
    with pytest.raises(ValidationError):
        HistoryEntry(ticket_id="t1", field_name=" ")
    e = HistoryEntry(ticket_id="t1", field_name="status", old_value="a", new_value="b")
    assert HistoryEntry.from_dict(e.to_dict()) == e
    assert "sistema" in str(e)

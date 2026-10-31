import pytest

from models.enums import Priority, Status, TicketType
from models.exceptions import ValidationError
from models.ticket import TITLE_MAX_LENGTH, Ticket


def test_defaults():
    t = Ticket(title="  Arreglar login  ")
    assert t.title == "Arreglar login"
    assert t.status == Status.NUEVO
    assert t.priority == Priority.MEDIA
    assert t.ticket_type == TicketType.TAREA
    assert not t.is_assigned and not t.is_closed
    assert len(t.id) == 32


def test_accepts_strings_and_converts_to_enums():
    t = Ticket(title="x", ticket_type="bug", priority="alta", status="revision")
    assert t.ticket_type is TicketType.BUG
    assert t.priority is Priority.ALTA
    assert t.status is Status.REVISION


@pytest.mark.parametrize("title", ["", "   ", None])
def test_empty_title_rejected(title):
    with pytest.raises(ValidationError):
        Ticket(title=title)


def test_title_too_long_rejected():
    with pytest.raises(ValidationError):
        Ticket(title="a" * (TITLE_MAX_LENGTH + 1))
    Ticket(title="a" * TITLE_MAX_LENGTH)  # el límite exacto sí se permite


@pytest.mark.parametrize(
    "kwargs", [{"priority": "urgentisima"}, {"status": "?"}, {"ticket_type": "epic"}]
)
def test_invalid_enum_values_rejected(kwargs):
    with pytest.raises(ValidationError):
        Ticket(title="x", **kwargs)


def test_change_status_and_touch():
    t = Ticket(title="x")
    before = t.updated_at
    t.change_status("en_progreso")
    assert t.status is Status.EN_PROGRESO
    assert t.updated_at >= before
    with pytest.raises(ValidationError):
        t.change_status("inexistente")


def test_close_ticket():
    t = Ticket(title="x")
    t.change_status(Status.HECHO)
    assert t.is_closed


def test_assign_and_unassign():
    t = Ticket(title="x")
    t.assign(" user_1 ")
    assert t.assignee_id == "user_1" and t.is_assigned
    t.unassign()
    assert t.assignee_id is None
    with pytest.raises(ValidationError):
        t.assign("  ")


def test_labels_are_normalized_and_unique():
    t = Ticket(title="x", labels=[" Backend ", "backend", "", "UI"])
    assert t.labels == ["backend", "ui"]
    t.add_label("API")
    t.add_label("api")
    assert t.labels == ["backend", "ui", "api"]
    t.remove_label("UI")
    assert t.labels == ["backend", "api"]
    with pytest.raises(ValidationError):
        t.add_label("  ")


def test_update_details():
    t = Ticket(title="viejo", description="d")
    t.update_details(title="nuevo")
    assert (t.title, t.description) == ("nuevo", "d")
    with pytest.raises(ValidationError):
        t.update_details(title="")


def test_dict_roundtrip():
    t = Ticket(title="x", ticket_type="bug", priority="critica", labels=["a"])
    t.assign("u1")
    assert Ticket.from_dict(t.to_dict()) == t


def test_to_dict_uses_plain_types():
    data = Ticket(title="x").to_dict()
    assert data["status"] == "nuevo"
    assert isinstance(data["created_at"], str)

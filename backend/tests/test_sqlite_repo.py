import copy

import pytest

from models.enums import Priority, Status, TicketType
from models.exceptions import (
    DuplicateError,
    ProjectNotFoundError,
    RepositoryError,
    TicketNotFoundError,
    UserNotFoundError,
)
from models.history import HistoryEntry, build_entries
from models.project import Project
from models.ticket import Ticket
from models.user import User
from storage import create_sqlite_storage
from storage.database import Database


# ---------------------------- Tickets ---------------------------------
def test_ticket_add_get_roundtrip(storage):
    t = Ticket(title="Bug ñandú", description="descripción", ticket_type="bug",
               priority="alta", labels=["ui", "api"])
    t.assign("u1")
    storage.tickets.add(t)
    assert storage.tickets.get(t.id) == t


def test_ticket_get_missing(storage):
    with pytest.raises(TicketNotFoundError):
        storage.tickets.get("no-existe")


def test_ticket_duplicate_id(storage):
    t = Ticket(title="x")
    storage.tickets.add(t)
    with pytest.raises(DuplicateError):
        storage.tickets.add(t)


def test_ticket_update(storage):
    t = storage.tickets.add(Ticket(title="x"))
    t.change_status("revision")
    t.add_label("urgente")
    storage.tickets.update(t)
    assert storage.tickets.get(t.id) == t


def test_ticket_update_and_delete_missing(storage):
    with pytest.raises(TicketNotFoundError):
        storage.tickets.update(Ticket(title="fantasma"))
    with pytest.raises(TicketNotFoundError):
        storage.tickets.delete("no-existe")


def test_ticket_delete(storage):
    t = storage.tickets.add(Ticket(title="x"))
    storage.tickets.delete(t.id)
    assert storage.tickets.list_all() == []


def test_list_all_keeps_creation_order(storage):
    titles = ["uno", "dos", "tres"]
    for title in titles:
        storage.tickets.add(Ticket(title=title))
    assert [t.title for t in storage.tickets.list_all()] == titles


@pytest.fixture
def populated(storage):
    a = Ticket(title="Login roto", description="No entra", ticket_type="bug",
               priority="alta", project_id="p1", assignee_id="u1")
    b = Ticket(title="Modo oscuro", ticket_type="feature", project_id="p1")
    c = Ticket(title="Documentar API", priority="baja", project_id="p2",
               assignee_id="u2", status="hecho")
    d = Ticket(title="Reporte 100% lento", description="usa guion_bajo",
               ticket_type="bug", assignee_id="u1", status="en_progreso")
    for t in (a, b, c, d):
        storage.tickets.add(t)
    return storage, {"a": a, "b": b, "c": c, "d": d}


def _titles(tickets):
    return sorted(t.title for t in tickets)


def test_find_by_each_filter(populated):
    st, t = populated
    assert _titles(st.tickets.find(status=Status.HECHO)) == ["Documentar API"]
    assert _titles(st.tickets.find(status="hecho")) == ["Documentar API"]
    assert _titles(st.tickets.find(priority=Priority.ALTA)) == ["Login roto"]
    assert len(st.tickets.find(ticket_type=TicketType.BUG)) == 2
    assert len(st.tickets.find(assignee_id="u1")) == 2
    assert len(st.tickets.find(project_id="p1")) == 2
    assert _titles(st.tickets.find(unassigned=True)) == ["Modo oscuro"]
    assert len(st.tickets.find(open_only=True)) == 3


def test_find_combines_filters(populated):
    st, _ = populated
    result = st.tickets.find(ticket_type="bug", assignee_id="u1", project_id="p1")
    assert _titles(result) == ["Login roto"]
    assert st.tickets.find(ticket_type="feature", assignee_id="u1") == []


def test_find_text_search(populated):
    st, _ = populated
    assert _titles(st.tickets.find(text="LOGIN")) == ["Login roto"]
    assert _titles(st.tickets.find(text="no entra")) == ["Login roto"]
    # los comodines de LIKE se tratan como texto literal
    assert _titles(st.tickets.find(text="100%")) == ["Reporte 100% lento"]
    assert _titles(st.tickets.find(text="guion_bajo")) == ["Reporte 100% lento"]
    assert st.tickets.find(text="%") == [st.tickets.find(text="100%")[0]]


def test_find_without_filters_returns_all(populated):
    st, _ = populated
    assert len(st.tickets.find()) == 4


def test_count_open_by_assignee(populated):
    st, _ = populated
    # u1: 2 abiertos | u2: su único ticket está HECHO | sin asignar: no cuenta
    assert st.tickets.count_open_by_assignee() == {"u1": 2}


# ---------------------------- Usuarios --------------------------------
def test_user_crud(storage):
    u = storage.users.add(User(name="Ana", email="ana@x.com", role="admin"))
    assert storage.users.get(u.id) == u
    assert storage.users.get_by_email("ANA@x.com") == u

    u.update_profile(name="Ana María")
    u.deactivate()
    storage.users.update(u)
    stored = storage.users.get(u.id)
    assert stored.name == "Ana María" and not stored.active

    storage.users.delete(u.id)
    with pytest.raises(UserNotFoundError):
        storage.users.get(u.id)


def test_user_errors(storage):
    storage.users.add(User(name="Ana", email="ana@x.com"))
    with pytest.raises(DuplicateError):
        storage.users.add(User(name="Otra Ana", email="ana@x.com"))
    with pytest.raises(UserNotFoundError):
        storage.users.get_by_email("nadie@x.com")
    with pytest.raises(UserNotFoundError):
        storage.users.update(User(name="Fantasma", email="f@x.com"))
    with pytest.raises(UserNotFoundError):
        storage.users.delete("no-existe")


def test_user_update_to_existing_email_is_duplicate(storage):
    storage.users.add(User(name="Ana", email="ana@x.com"))
    luis = storage.users.add(User(name="Luis", email="luis@x.com"))
    luis.update_profile(email="ana@x.com")
    with pytest.raises(DuplicateError):
        storage.users.update(luis)


def test_user_list_active_only(storage):
    storage.users.add(User(name="Ana", email="a@x.com"))
    inactive = User(name="Luis", email="l@x.com")
    inactive.deactivate()
    storage.users.add(inactive)
    assert len(storage.users.list_all()) == 2
    assert [u.name for u in storage.users.list_all(active_only=True)] == ["Ana"]


# ---------------------------- Proyectos -------------------------------
def test_project_crud(storage):
    p = storage.projects.add(
        Project(name="Titan", key="tit", owner_id="u1", member_ids=["u2"])
    )
    assert storage.projects.get(p.id) == p
    assert storage.projects.get_by_key("tit") == p

    p.add_member("u3")
    p.archive()
    storage.projects.update(p)
    stored = storage.projects.get(p.id)
    assert stored.member_ids == ["u2", "u1", "u3"] and not stored.active

    storage.projects.delete(p.id)
    with pytest.raises(ProjectNotFoundError):
        storage.projects.get(p.id)


def test_project_errors(storage):
    storage.projects.add(Project(name="A", key="AA"))
    with pytest.raises(DuplicateError):
        storage.projects.add(Project(name="B", key="aa"))
    with pytest.raises(ProjectNotFoundError):
        storage.projects.get_by_key("ZZ")
    with pytest.raises(ProjectNotFoundError):
        storage.projects.update(Project(name="C", key="CC"))
    with pytest.raises(ProjectNotFoundError):
        storage.projects.delete("no-existe")


def test_project_list_active_only(storage):
    storage.projects.add(Project(name="A", key="AA"))
    old = Project(name="B", key="BB")
    old.archive()
    storage.projects.add(old)
    assert len(storage.projects.list_all()) == 2
    assert [p.key for p in storage.projects.list_all(active_only=True)] == ["AA"]


# ---------------------------- Historial -------------------------------
def test_history_end_to_end(storage):
    ticket = storage.tickets.add(Ticket(title="Bug"))
    storage.history.add(HistoryEntry.for_creation(ticket, changed_by="u1"))

    old = storage.tickets.get(ticket.id)
    new = storage.tickets.get(ticket.id)
    new.change_status("en_progreso")
    new.assign("u2")
    storage.tickets.update(new)
    storage.history.add_many(build_entries(old, new, changed_by="u1"))

    history = storage.history.list_for_ticket(ticket.id)
    assert [e.field_name for e in history] == ["created", "status", "assignee_id"]
    assert all(e.changed_by == "u1" for e in history)
    assert history[1].old_value == "nuevo" and history[1].new_value == "en_progreso"


def test_history_empty_and_isolated_per_ticket(storage):
    assert storage.history.list_for_ticket("nada") == []
    storage.history.add_many([])  # no debe fallar
    storage.history.add(HistoryEntry(ticket_id="t1", field_name="status"))
    storage.history.add(HistoryEntry(ticket_id="t2", field_name="status"))
    assert len(storage.history.list_for_ticket("t1")) == 1


def test_history_add_many_is_atomic(storage):
    first = HistoryEntry(ticket_id="t1", field_name="status")
    clone = copy.deepcopy(first)  # mismo id -> choca en la segunda fila
    with pytest.raises(DuplicateError):
        storage.history.add_many([first, clone])
    assert storage.history.list_for_ticket("t1") == []  # no quedó nada a medias


# ---------------------------- Base de datos ---------------------------
def test_data_persists_between_connections(tmp_path):
    path = tmp_path / "sub" / "tickets.db"  # la carpeta se crea sola
    st = create_sqlite_storage(path)
    ticket = st.tickets.add(Ticket(title="Persistente", labels=["x"]))
    st.close()

    reopened = create_sqlite_storage(path)
    assert reopened.tickets.get(ticket.id) == ticket
    reopened.close()


def test_database_reopens_after_close(tmp_path):
    st = create_sqlite_storage(tmp_path / "t.db")
    t = st.tickets.add(Ticket(title="x"))
    st.close()
    assert st.tickets.get(t.id).title == "x"  # se reabre sola
    st.close()


def test_unopenable_database_raises_repository_error(tmp_path):
    blocker = tmp_path / "archivo"
    blocker.write_text("no soy una carpeta")
    db = Database(blocker / "tickets.db")  # el "padre" es un archivo
    with pytest.raises(RepositoryError):
        db.fetch_all("SELECT 1")

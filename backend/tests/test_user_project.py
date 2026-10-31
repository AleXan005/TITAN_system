import pytest

from models.enums import UserRole
from models.exceptions import ValidationError
from models.project import Project
from models.user import User


# ---------------------------- User ------------------------------------
def test_user_normalizes_data():
    u = User(name="  Ana  ", email=" Ana@Correo.COM ")
    assert u.name == "Ana"
    assert u.email == "ana@correo.com"
    assert u.role is UserRole.DESARROLLADOR


@pytest.mark.parametrize("email", ["", "sin-arroba", "a@b", "a b@c.com", None])
def test_user_invalid_email(email):
    with pytest.raises(ValidationError):
        User(name="Ana", email=email)


def test_user_invalid_name_and_role():
    with pytest.raises(ValidationError):
        User(name=" ", email="a@b.com")
    with pytest.raises(ValidationError):
        User(name="Ana", email="a@b.com", role="dios")


def test_user_assignability():
    dev = User(name="Dev", email="d@x.com")
    rep = User(name="Rep", email="r@x.com", role="reportador")
    assert dev.can_be_assigned
    assert not rep.can_be_assigned
    dev.deactivate()
    assert not dev.can_be_assigned
    dev.activate()
    assert dev.can_be_assigned


def test_user_roundtrip():
    u = User(name="Ana", email="a@b.com", role="admin")
    assert User.from_dict(u.to_dict()) == u
    assert u.is_admin


# ---------------------------- Project ---------------------------------
def test_project_key_is_uppercased():
    p = Project(name="Titan", key="tit")
    assert p.key == "TIT"


@pytest.mark.parametrize("key", ["", "A", "1AB", "AB CD", "A" * 11, "AB-C"])
def test_project_invalid_key(key):
    with pytest.raises(ValidationError):
        Project(name="x", key=key)


def test_project_owner_is_member():
    p = Project(name="x", key="XX", owner_id="u1", member_ids=["u2", "u2"])
    assert p.member_ids == ["u2", "u1"]
    assert p.has_member("u1") and p.member_count == 2


def test_project_members_management():
    p = Project(name="x", key="XX", owner_id="u1")
    p.add_member("u2")
    p.add_member("u2")
    assert p.member_count == 2
    p.remove_member("u2")
    assert not p.has_member("u2")
    with pytest.raises(ValidationError):
        p.remove_member("u1")  # el dueño no se puede quitar


def test_project_change_owner():
    p = Project(name="x", key="XX", owner_id="u1")
    p.change_owner("u3")
    assert p.owner_id == "u3" and p.has_member("u3")
    p.remove_member("u1")  # ya no es dueño


def test_project_archive_and_roundtrip():
    p = Project(name="x", key="XX", owner_id="u1")
    p.archive()
    assert not p.active
    assert Project.from_dict(p.to_dict()) == p

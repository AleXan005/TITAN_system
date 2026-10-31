import json
import logging

import pytest

from config import Settings, load_settings
from models.exceptions import ConfigError
from utils.logger import LOG_FILE_NAME, ROOT_LOGGER_NAME, get_logger, setup_logging


def _load(tmp_path, *, json_data=None, env_text=None, environ=None):
    json_file = tmp_path / "config.json"
    env_file = tmp_path / ".env"
    if json_data is not None:
        json_file.write_text(json.dumps(json_data), encoding="utf-8")
    if env_text is not None:
        env_file.write_text(env_text, encoding="utf-8")
    return load_settings(json_file, env_file, environ=environ or {})


# ---------------------------- Config ----------------------------------
def test_defaults_when_no_files(tmp_path):
    s = _load(tmp_path)
    assert s == Settings()
    assert s.log_level == "INFO" and s.log_to_file is True


def test_priority_json_then_env_file_then_environ(tmp_path):
    s = _load(
        tmp_path,
        json_data={"db_path": "json.db", "log_level": "warning", "app_env": "json"},
        env_text="TICKETS_DB_PATH=envfile.db\nTICKETS_APP_ENV=envfile\n",
        environ={"TICKETS_APP_ENV": "real"},
    )
    assert s.log_level == "WARNING"      # solo está en el JSON (y se normaliza)
    assert s.db_path == "envfile.db"     # .env gana al JSON
    assert s.app_env == "real"           # variable de entorno gana a todo


def test_env_file_syntax(tmp_path):
    s = _load(
        tmp_path,
        env_text=(
            "# comentario\n\n"
            "export TICKETS_DB_PATH='con espacios.db'\n"
            'TICKETS_LOG_DIR="mis logs"\n'
            "OTRA_COSA=ignorada\n"
        ),
    )
    assert s.db_path == "con espacios.db"
    assert s.log_dir == "mis logs"


@pytest.mark.parametrize(
    "raw,expected",
    [("true", True), ("1", True), ("Sí", True), ("no", False), ("0", False), ("OFF", False)],
)
def test_bool_parsing(tmp_path, raw, expected):
    s = _load(tmp_path, environ={"TICKETS_LOG_TO_FILE": raw})
    assert s.log_to_file is expected


def test_invalid_values_raise_config_error(tmp_path):
    with pytest.raises(ConfigError):
        _load(tmp_path, environ={"TICKETS_LOG_LEVEL": "ruidoso"})
    with pytest.raises(ConfigError):
        _load(tmp_path, environ={"TICKETS_LOG_TO_FILE": "quizas"})
    with pytest.raises(ConfigError):
        _load(tmp_path, environ={"TICKETS_DB_PATH": "  "})


def test_bad_json_raises_config_error(tmp_path):
    (tmp_path / "config.json").write_text("{ no es json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_settings(tmp_path / "config.json", tmp_path / ".env", environ={})


def test_unknown_json_key_raises_config_error(tmp_path):
    with pytest.raises(ConfigError):
        _load(tmp_path, json_data={"db_pth": "typo.db"})


def test_settings_are_immutable():
    with pytest.raises(Exception):
        Settings().db_path = "otro"


# ---------------------------- Logger ----------------------------------
@pytest.fixture
def clean_root_logger():
    root = logging.getLogger(ROOT_LOGGER_NAME)
    saved = (list(root.handlers), root.level, root.propagate)
    yield root
    for h in list(root.handlers):
        root.removeHandler(h)
        h.close()
    for h in saved[0]:
        root.addHandler(h)
    root.setLevel(saved[1])
    root.propagate = saved[2]


def test_get_logger_names():
    assert get_logger("storage.database").name == "ticket_automator.storage.database"
    assert get_logger("ticket_automator.x").name == "ticket_automator.x"


def test_setup_logging_writes_file(tmp_path, clean_root_logger):
    settings = Settings(log_dir=str(tmp_path / "logs"), log_to_console=False,
                        log_level="INFO")
    setup_logging(settings)
    get_logger("tests").info("mensaje de prueba")
    get_logger("tests").debug("no debe aparecer")
    for h in clean_root_logger.handlers:
        h.flush()
    content = (tmp_path / "logs" / LOG_FILE_NAME).read_text(encoding="utf-8")
    assert "mensaje de prueba" in content
    assert "ticket_automator.tests" in content
    assert "no debe aparecer" not in content


def test_setup_logging_twice_does_not_duplicate_handlers(tmp_path, clean_root_logger):
    settings = Settings(log_dir=str(tmp_path / "logs"))
    setup_logging(settings)
    setup_logging(settings)
    assert len(clean_root_logger.handlers) == 2  # consola + archivo


def test_logging_disabled_uses_null_handler(tmp_path, clean_root_logger):
    setup_logging(Settings(log_to_file=False, log_to_console=False))
    assert [type(h).__name__ for h in clean_root_logger.handlers] == ["NullHandler"]

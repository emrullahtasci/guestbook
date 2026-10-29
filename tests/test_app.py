import pytest

from app import create_app
from app.models import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )
    app.config["LOG_FILE"] = tmp_path / "app.log"
    with app.test_client() as client:
        client.application = app
        yield client
    with app.app_context():
        db.drop_all()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_empty_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"No messages yet" in res.data


def test_submit_message_is_listed(client):
    res = client.post(
        "/", data={"name": "Emrullah", "message": "Hello Docker"}, follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Emrullah" in res.data
    assert b"Hello Docker" in res.data
    assert b"Messages (1)" in res.data


def test_empty_form_is_rejected(client):
    res = client.post("/", data={"name": " ", "message": ""}, follow_redirects=True)
    assert b"Name and message are both required." in res.data
    assert b"Messages (0)" in res.data


def test_message_is_logged(client):
    client.post("/", data={"name": "Logger", "message": "hi"})
    log = client.application.config["LOG_FILE"].read_text()
    assert "New message saved from Logger" in log

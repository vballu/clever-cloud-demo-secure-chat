"""Tests of the secure chat demo, without Keycloak nor PostgreSQL (SQLite in memory)."""
import importlib
import os
import sys

import pytest


def load_app(monkeypatch, **env):
    for key in ("SECRET_KEY", "SESSION_COOKIE_SECURE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("POSTGRESQL_ADDON_URI", "sqlite:///:memory:")
    monkeypatch.setenv("CC_KEYCLOAK_URL", "https://keycloak.example.com")
    monkeypatch.setenv("KEYCLOAK_REALM", "demo")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # Ignore any local .env file: the tests control the environment themselves.
    import dotenv
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: False)
    sys.modules.pop("main", None)
    return importlib.import_module("main")


def test_refuses_to_start_without_secret_key(monkeypatch):
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_app(monkeypatch)


def test_secure_cookies_by_default(monkeypatch):
    main = load_app(monkeypatch, SECRET_KEY="test-only-not-a-real-key")
    assert main.app.config["SESSION_COOKIE_SECURE"] is True
    assert main.app.config["SESSION_COOKIE_HTTPONLY"] is True


def test_insecure_cookies_only_when_asked(monkeypatch):
    main = load_app(monkeypatch, SECRET_KEY="test-only-not-a-real-key", SESSION_COOKIE_SECURE="false")
    assert main.app.config["SESSION_COOKIE_SECURE"] is False


@pytest.fixture
def client(monkeypatch):
    main = load_app(monkeypatch, SECRET_KEY="test-only-not-a-real-key", SESSION_COOKIE_SECURE="false")
    return main.app.test_client()


def test_home_page(client):
    assert client.get("/").status_code == 200


def test_messages_require_sign_in(client):
    assert client.get("/messages").status_code == 401
    assert client.post("/messages", json={"contenu": "hello"}).status_code == 401


def sign_in(client):
    with client.session_transaction() as s:
        s["user"] = {"username": "alice", "email": "alice@example.com", "name": "Alice"}


def test_post_and_read_message(client):
    sign_in(client)
    assert client.post("/messages", json={"contenu": " hello "}).status_code == 200
    messages = client.get("/messages").get_json()
    assert messages[-1]["pseudo"] == "alice"
    assert messages[-1]["contenu"] == "hello"


def test_rejects_empty_and_too_long_messages(client):
    sign_in(client)
    assert client.post("/messages", json={"contenu": "   "}).status_code == 400
    assert client.post("/messages", json={}).status_code == 400
    assert client.post("/messages", json={"contenu": "x" * 2001}).status_code == 400

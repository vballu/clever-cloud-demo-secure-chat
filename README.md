# Secure chat on Clever Cloud

A small chat application protected by Keycloak, deployed on Clever Cloud in a few commands. It shows how to plug managed authentication and a managed PostgreSQL database into a Python application, with no server to run yourself.

## What it shows

- **Authentication delegated to Keycloak** (OpenID Connect, through Authlib): users sign in with Keycloak, the application never handles passwords.
- **Messages stored in PostgreSQL** (Flask-SQLAlchemy): the last 50 messages are shown.
- **Configuration by environment variables only**: the add-ons inject their credentials, nothing secret lives in the code.

## Deploy on Clever Cloud

Requirements: a Clever Cloud account and [Clever Tools](https://www.clever.cloud/developers/doc/cli/).

```bash
clever create --type python secure-chat
clever addon create postgresql-addon secure-chat-db --link secure-chat
clever addon create keycloak secure-chat-keycloak --link secure-chat
```

In the Keycloak console, create a realm and an OpenID Connect client with the redirect URI `https://<your-app-domain>/authorize`, then set:

```bash
clever env set KEYCLOAK_REALM <realm>
clever env set KEYCLOAK_CLIENT_ID <client-id>
clever env set KEYCLOAK_CLIENT_SECRET <client-secret>
clever env set SECRET_KEY "$(openssl rand -hex 32)"
clever env set CC_RUN_COMMAND "uv run flask --app main run --host 0.0.0.0 --port 8080"
clever deploy
```

`POSTGRESQL_ADDON_URI` is provided by the PostgreSQL add-on. The application reads the Keycloak address from `CC_KEYCLOAK_URL`: check with `clever env` that the Keycloak add-on provides it, or set it yourself.

## Run locally

```bash
uv sync
export POSTGRESQL_ADDON_URI=postgresql://localhost/minichat
export CC_KEYCLOAK_URL=<keycloak-url> KEYCLOAK_REALM=<realm> KEYCLOAK_CLIENT_ID=<id> KEYCLOAK_CLIENT_SECRET=<secret>
export SECRET_KEY=dev
uv run flask --app main run
```

## Endpoints

| Route | Purpose |
|---|---|
| `/` | Chat page |
| `/login`, `/authorize`, `/logout` | Keycloak sign-in flow |
| `/user` | Signed-in user, as JSON |
| `/messages` | Read (GET) or post (POST) messages, signed-in users only |

## Status

Demonstration code, used in Clever Cloud workshops. Not intended for production as is: set a strong `SECRET_KEY` and secure cookies behind HTTPS.

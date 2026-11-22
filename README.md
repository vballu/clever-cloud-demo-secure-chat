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
clever env set CC_PYTHON_VERSION 3.13
clever env set CC_PYTHON_MODULE main:app
clever deploy
```

`POSTGRESQL_ADDON_URI` is provided by the PostgreSQL add-on. The application reads the Keycloak address from `CC_KEYCLOAK_URL`: check with `clever env` that the Keycloak add-on provides it, or set it yourself.

## Deploy with Terraform or OpenTofu

`terraform/main.tf` creates the PostgreSQL database and the Python application (auto-scaling from 1 to 3 instances), and deploys this repository:

```bash
cd terraform
terraform init
terraform apply -var organisation=<orga_or_user_id> -var secret_key="$(openssl rand -hex 32)"
```

Keycloak still needs the realm and client described above, and the `KEYCLOAK_*` variables on the application.

## Run locally

```bash
uv sync
export POSTGRESQL_ADDON_URI=postgresql://localhost/minichat
export CC_KEYCLOAK_URL=<keycloak-url> KEYCLOAK_REALM=<realm> KEYCLOAK_CLIENT_ID=<id> KEYCLOAK_CLIENT_SECRET=<secret>
export SECRET_KEY=dev SESSION_COOKIE_SECURE=false  # local run over HTTP only
uv run flask --app main run
```

## Tests

```bash
uv run --group dev pytest
```

The tests use SQLite in memory and need neither Keycloak nor PostgreSQL. They check that the application refuses to start without `SECRET_KEY`, that cookies are secure by default, that messages require sign-in, and that empty or overlong messages are rejected.

## Endpoints

| Route | Purpose |
|---|---|
| `/` | Chat page |
| `/login`, `/authorize`, `/logout` | Keycloak sign-in flow |
| `/user` | Signed-in user, as JSON |
| `/messages` | Read (GET) or post (POST) messages, signed-in users only |

## Security choices

- No default secret: the application refuses to start without `SECRET_KEY`.
- Session cookies are `Secure`, `HttpOnly` and `SameSite=Lax` by default.
- Behind the Clever Cloud load balancers, `ProxyFix` trusts `X-Forwarded-Proto` so that the Keycloak redirect URI uses HTTPS.
- Messages are trimmed and limited to 2,000 characters.

## Status

Demonstration code, used in Clever Cloud workshops.

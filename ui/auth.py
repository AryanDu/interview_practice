"""Google OIDC login gate for the multi-user Streamlit app.

The app fails closed until Google OIDC and PostgreSQL are configured. User IDs are
stable pseudonymous hashes of the OIDC issuer + subject, so email addresses are
not stored in quiz history rows.
"""
from __future__ import annotations

import hashlib
import os

import streamlit as st


def _secret(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value.strip()
    try:
        secret_value = st.secrets.get(name, default)
        if secret_value:
            return str(secret_value).strip()
    except Exception:
        pass
    return default


def _auth_settings() -> dict:
    try:
        value = st.secrets.get("auth", {})
        return dict(value) if value else {}
    except Exception:
        return {}


def _show_setup_help(missing_auth: list[str], missing_database: bool, missing_allowlist: bool = False) -> None:
    st.title("🔐 Interview Practice — setup required")
    st.write("Multi-user sign-in and isolated progress are enabled in this version, but deployment secrets are not configured yet.")
    if missing_auth:
        st.error("Google sign-in is not configured. Add the required values in Streamlit App → Settings → Secrets.")
        st.markdown(
            "Create an OAuth 2.0 **Web application** client in Google Cloud and add the Streamlit app URL "
            "as an authorized redirect URI. Use the exact callback URL shown below."
        )
    if missing_database:
        st.error("DATABASE_URL is missing. Create a PostgreSQL database (for example in Neon) and paste its SSL connection string above the [auth] section.")
    if missing_allowlist:
        st.error("ALLOWED_EMAILS is required for this public app. Add the comma-separated Google accounts allowed to use it.")
    if missing_auth or missing_database or missing_allowlist:
        setup_example = chr(10).join([
            'DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"',
            'ALLOWED_EMAILS = "you@example.com,friend@example.com"  # Required allowlist',
            "",
            "[auth]",
            'redirect_uri = "https://interview-practice-by-aryan.streamlit.app/oauth2callback"',
            'cookie_secret = "PASTE_A_LONG_RANDOM_SECRET_HERE"',
            'client_id = "GOOGLE_OAUTH_CLIENT_ID"',
            'client_secret = "GOOGLE_OAUTH_CLIENT_SECRET"',
            'server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"',
        ])
        st.code(setup_example, language="toml")
        st.caption("Keep the database URL, OAuth client secret, and cookie secret private. Never commit them to GitHub.")
        if missing_auth:
            st.caption("Missing Google OIDC settings: " + ", ".join(missing_auth))
    st.markdown("Setup guide: [Google OIDC and PostgreSQL](https://github.com/AryanDu/interview_practice/blob/main/docs/MULTI_USER_SETUP.md)")
    st.stop()


def require_authenticated_user() -> dict:
    """Require a Google-authenticated user and return a stable app-scoped ID."""
    settings = _auth_settings()
    required = ("redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url")
    missing = [key for key in required if not str(settings.get(key, "")).strip()]
    database_url = _secret("DATABASE_URL")
    allowed_emails = _secret("ALLOWED_EMAILS")
    allowlist = {item.strip().lower() for item in allowed_emails.split(",") if item.strip()}
    if missing or not database_url or not allowlist:
        _show_setup_help(missing, not bool(database_url), not bool(allowlist))

    try:
        logged_in = bool(st.user.is_logged_in)
    except Exception:
        logged_in = False

    if not logged_in:
        st.title("💼 Interview Practice App")
        st.write("Sign in with Google to access your quizzes and save your own progress.")
        st.button("Continue with Google", type="primary", on_click=st.login, use_container_width=True)
        st.caption("Each signed-in account has its own quiz history, goals, and progress.")
        st.stop()

    claims = dict(st.user)
    email = str(claims.get("email", "")).strip().lower()
    subject = str(claims.get("sub", "")).strip()
    issuer = str(claims.get("iss", "google")).strip()
    verified = claims.get("email_verified")
    if not email or not subject or str(verified).lower() != "true":
        st.error("Google did not provide a verified email and stable user identifier. Please sign out and try another Google account.")
        if st.button("Sign out"):
            st.logout()
        st.stop()

    if email not in allowlist:
            st.error("This Google account is not on the app's access list. Ask the app owner to allow your email.")
            if st.button("Sign out"):
                st.logout()
            st.stop()

    user_id = hashlib.sha256(f"{issuer}:{subject}".encode("utf-8")).hexdigest()
    st.session_state["auth_user_id"] = user_id
    st.session_state["auth_email"] = email
    st.session_state["auth_name"] = str(claims.get("name") or email.split("@")[0])
    return {"id": user_id, "email": email, "name": st.session_state["auth_name"]}

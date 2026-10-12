# Multi-user setup (Google Sign-in + PostgreSQL)

This version uses Streamlit's native OpenID Connect (OIDC) login and PostgreSQL so each account has isolated progress. It intentionally fails closed until deployment secrets are configured.

## 1. Create the PostgreSQL database

1. Create a project in [Neon Console](https://console.neon.tech/).
2. Open **Connect** and copy the PostgreSQL connection string. Prefer the pooled connection string if Neon displays one for your project.
3. Keep the string private. Do not place it in the repository or send it in chat.

The app automatically creates/migrates its tables (quiz_attempts, quiz_responses, and user_settings) at first connection. It uses a shared connection pool capped at 10 connections.

## 2. Configure Google Sign-in

1. Open [Google Cloud Console](https://console.cloud.google.com/), choose/create a project, and configure Google Auth Platform / OAuth consent.
2. Create an OAuth client ID with application type **Web application**.
3. Add this exact **Authorized redirect URI**:

   https://interview-practice-by-aryan.streamlit.app/oauth2callback

4. Copy the OAuth client ID and client secret. If the consent screen is still in Testing mode, add the intended users as test users; otherwise Google's consent/publishing requirements may block sign-in for them.

Streamlit's built-in OIDC handles login cookies and identity-token validation. The database stores a SHA-256 hash derived from the OIDC issuer and subject instead of storing email addresses in quiz attempt rows.

## 3. Add secrets to Streamlit Community Cloud

Open the app's **Settings → Secrets** and add the following TOML. Replace placeholders with real values. The DATABASE_URL and ALLOWED_EMAILS lines must be placed **before** the [auth] heading so they stay at the top level.

    DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"
    ALLOWED_EMAILS = "aryan@gmail.com,friend1@gmail.com,friend2@gmail.com"

    [auth]
    redirect_uri = "https://interview-practice-by-aryan.streamlit.app/oauth2callback"
    cookie_secret = "PASTE_A_LONG_RANDOM_SECRET_HERE"
    client_id = "GOOGLE_OAUTH_CLIENT_ID"
    client_secret = "GOOGLE_OAUTH_CLIENT_SECRET"
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

- Use the real Postgres URI from Neon, including its SSL parameters.
- Create a long random cookie_secret; do not reuse the OAuth client secret.
- ALLOWED_EMAILS is optional. If set, only comma-separated addresses on that list may enter. Leave it as an empty string only if you intend to allow any Google account to sign in.
- The app uses one shared Gemini API key for question generation. For a 50–60 person group, restrict access with ALLOWED_EMAILS and monitor Gemini quota; all users share the provider's quota.
- Never commit this secrets block to GitHub or post it publicly.

## 4. What users see

- Users sign in with Google; no password database or reset flow is needed.
- Each logged-in user gets a stable pseudonymous internal ID based on their OIDC identity.
- Quiz attempts, answer review, topic charts, daily goals, and streaks are filtered to that ID. Daily goals are stored per user.
- The dashboard reads progress automatically. Users do not need to upload CSV files.
- Sign-out is available in the sidebar.

## 5. Important migration and access notes

- The previous SQLite history is not automatically copied to Neon. If the old SQLite file still exists and its rows need preserving, migrate it separately after deciding which account owns that history. Do not assign legacy history to whichever user signs in first.
- SQLite remains available only as a local development fallback. The deployed multi-user app requires DATABASE_URL, so it cannot silently fall back to an ephemeral shared cloud database.
- The repository changes can be tested locally, but end-to-end login/database testing requires real Google OAuth credentials and a working Neon database.
- For a private group of 50–60 users, populate ALLOWED_EMAILS with their Google account addresses. Without the allowlist, any Google account can sign in.

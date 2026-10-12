# Security hardening notes

## Public deployment baseline

- Google OIDC is required; report and quiz history are scoped to the pseudonymous authenticated user ID.
- The public deployment must configure a non-empty `ALLOWED_EMAILS` allowlist, a PostgreSQL `DATABASE_URL`, and the documented OIDC values. Do not commit secrets to this repository.
- Account changes clear old Streamlit session state (chat history, current mock interview/report and cached vector/LLM objects) before the new account's UI is rendered.
- Streamlit detailed error display is disabled. User/AI-controlled text used in custom Chat Assistant and result-card HTML is HTML-escaped; PDF text is escaped and length-bounded; app-facing provider errors are generic while detailed exceptions go to server logs.
- The checked-in generated Chroma vector database was removed. The runtime vector database path is now scoped to a SHA-256-derived per-user directory; new database files are ignored by Git.
- Vector document identifiers use SHA-256 instead of MD5.
- SecurityGuard request limits are shared across sessions within a single Python process and use a lock; they are not a distributed quota across multiple Cloud replicas. Provider-side quotas and persistent/distributed rate limiting are still needed for a horizontally scaled deployment.

## ChromaDB advisory exception (reviewed 2026-10-13)

`pip-audit` currently reports these advisories for the latest available `chromadb` release in the Python dependency set: `PYSEC-2026-311`, `PYSEC-2026-3813`, `PYSEC-2026-3814`, and `PYSEC-2026-3815`. The upstream advisory records currently list no patched release. The affected attack surfaces describe Chroma's HTTP/server API routes and authorization; this app uses `chromadb.PersistentClient` in-process and does not start `chroma run`, a Chroma HTTP server, or an `HttpClient`. The CI audit ignores only these specific advisories while this deployment uses the embedded client. This is a context-specific risk acceptance, **not** a claim that the package is vulnerability-free.

**Do not start or expose a Chroma server, enable Chroma HTTP endpoints, or use the vulnerable authorization modes in this application.** Re-check the upstream advisories before every ChromaDB upgrade and remove the CI ignores as soon as a patched release is available. If the architecture changes to use Chroma server/API, these ignores are no longer valid and must be removed before release.

## Automated security controls

The CI workflow compiles the app, runs every automated test file matching `tests/test_*.py` (including a 60-identity, 12-worker SQLite concurrency/isolation smoke test), performs Bandit scanning, audits dependencies with the narrowly documented ChromaDB exception, and scans Git history for accidentally committed secrets using Gitleaks. The synthetic SQLite test is not a production PostgreSQL load test.

A clean current tree does not erase an earlier file from public Git history. If Gitleaks finds a real credential, revoke/rotate it first; history rewrite and cache/clone cleanup may also be necessary.

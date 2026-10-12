# Quiz Studio & Progress Tracker

The Quiz & Progress Tracker module supports these workflows:

- **Topic quizzes:** generate 5–20 multiple-choice questions from a topic at Easy, Medium, or Hard difficulty.
- **Notes-based quizzes:** paste study material or upload a text-based PDF, TXT, or Markdown file. Scanned PDFs without extractable text are not OCR-processed.
- **Retry and fallback:** transient Gemini errors (including 429/503) trigger a bounded retry and fallback through the configured stable Flash model IDs. API-key/permission errors are shown separately.
- **Timed mock tests:** choose a time limit; answers are autosaved to Streamlit session state as each radio selection changes, and the test auto-submits when the timer expires.
- **Answer review:** scores, correct answers, explanations, and unanswered questions are shown after submission.
- **Automatic attempt history:** score, difficulty, mode, response choices, answer keys, topics, and explanations are stored in SQLite; CSV is optional backup only.
- **Progress dashboard:** overall accuracy, question counts, topic-level accuracy charts, weaker/stronger topic signals, daily goal, and streaks.
- **Weak-topic practice:** once a topic has at least three recorded responses, generate a short fresh quiz focused on it.

## Configuration

Set GEMINI_API_KEY in Streamlit Community Cloud → App settings → Secrets, or as a local environment variable. The module also reads GOOGLE_API_KEY for compatibility.

Additional dependencies used by this module:

- pypdf for text extraction from PDF study notes.
- streamlit-autorefresh for the live timer in a timed mock test.

## Storage and privacy status

SQLite is the current implementation so storage can be revisited later. Its database is placed in the app's local data/ directory by default, with an optional QUIZ_TRACKER_DB_PATH override. Streamlit Cloud's local filesystem is not a durable-storage guarantee, so history may be reset by some restarts or redeployments. The database remains a local app file; the final persistent-storage design is intentionally not selected yet.

This app is configured for one personal profile (QUIZ_PROFILE_ID can override the profile key). Until access protection is configured, anyone who can use the public app URL may share the same profile/history. Do not use a public deployment for sensitive study notes or private data without adding access control.

#!/usr/bin/env python3
"""CLI helper to show where LLM API keys are coming from and masked values.

Usage:
  python scripts/debug_keys.py

This inspects (in order):
 - .streamlit/secrets.toml (if present and importable via streamlit)
 - .env file in project root
 - environment variables

It prints a short report with masked values and source.
"""
import os
from pathlib import Path
import toml

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / '.env'
STREAMLIT_SECRETS = ROOT / '.streamlit' / 'secrets.toml'

VAR_MAP = {
    'openai': 'OPENAI_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'claude': 'ANTHROPIC_API_KEY',
    'grok': 'GROK_API_KEY',
    'ollama': 'OLLAMA_BASE_URL',
}


def load_env_file(path: Path):
    data = {}
    if not path.exists():
        return data
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return data


def load_streamlit_secrets(path: Path):
    if not path.exists():
        return {}
    try:
        return toml.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def mask(val: str) -> str:
    if not val:
        return ''
    s = str(val)
    if len(s) <= 8:
        return '***'
    return s[:3] + '...' + s[-4:]


def main():
    env_vals = load_env_file(ENV_FILE)
    secrets = load_streamlit_secrets(STREAMLIT_SECRETS)

    print('\nLLM API Key Sources Report')
    print('Root: {}'.format(ROOT))
    print('Checking .streamlit/secrets.toml: {}' .format('found' if STREAMLIT_SECRETS.exists() else 'not found'))
    print('Checking .env: {}' .format('.env found' if ENV_FILE.exists() else 'not found'))

    for provider, var in VAR_MAP.items():
        source = None
        value = None

        # streamlit secrets
        if var in secrets and secrets.get(var):
            source = 'streamlit_secrets'
            value = secrets.get(var)

        # .env file
        if not source and var in env_vals and env_vals.get(var):
            source = '.env'
            value = env_vals.get(var)

        # environment
        if not source and os.getenv(var):
            source = 'environment'
            value = os.getenv(var)

        if source:
            print(f"- {provider}: {source} -> {mask(value)}")
        else:
            print(f"- {provider}: not set")


if __name__ == '__main__':
    main()

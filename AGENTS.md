# AGENTS.md — NebulaShell

## Quick start

```bash
pip install -r requirements.txt
python -m oss.cli serve              # start server on :8080
# or: python main.py
# or: oss serve (after pip install -e .)
```

## Architecture (minimal core philosophy)

- Core framework (`oss/`) loads only **one** builtin plugin: `store/@{NebulaShell}/plugin-loader/`
- `plugin-loader` then scans `store/@{NebulaShell}/` and manages all other plugins
- Two store namespaces: `@{NebulaShell}` (26 official plugins) and `@{Falck}` (2 plugins)
- Entry point: `oss/cli.py:main()` → `PluginManager` → `PluginLoader.load_core_plugin("plugin-loader")`
- Each store plugin at `store/@{NebulaShell}/<name>/main.py` must export a `New()` factory function
- Plugin base class: `oss/plugin/types.py:Plugin` (abstract: `init`, `start`, `stop`)

## Commands

| Action | Command |
|--------|---------|
| Start server | `python -m oss.cli serve` |
| Show info | `python -m oss.cli info` |
| Hidden achievements | Prefix with `!!` (e.g., `!!help`, `!!list`, `!!stats`, `!!debug`) |
| Docker | `docker-compose up` (ports 8080-8082) |

Hidden commands defined in `oss/core/achievements.py` — they are a gamification layer, not real administration.

## Config

- **`oss.config.json`** — runtime config (port, host, data/store dirs, log level, permissions)
- Priority: env var > `oss.config.json` > hardcoded defaults (`oss/config/config.py`)
- Must set `PYTHONPATH` to repo root before running anything
- `PYTHONUNBUFFERED=1` recommended for dev

## Test

```bash
pytest -v --tb=short          # single test file: oss/tests/test_nodejs_adapter.py
```

Tests require Node.js/npm on `$PATH` or many tests skip. No CI workflows exist.

## Toolchain

```
black oss/ store/@{NebulaShell}/   # formatter (line-length=88)
pylint oss/ store/@{NebulaShell}/  # linter (references .pylintrc, file may not exist)
```

No typechecker configured. No CI.

## Rename history

This project was renamed from **FutureOSS** → **NebulaShell**. Old name may still appear in git history, external URLs, or stale wiki references. Always use "NebulaShell" in new code.

## Ports

| Port | Service |
|------|---------|
| 8080 | HTTP API + WebUI |
| 8081 | WebSocket |
| 8082 | HTTP TCP |

# AGENTS

## Project Purpose

This project is a backend/frontend system for managing DIY hardware and electronics stock. The current focus is on inventory management and label printing, with planned extensions for DIY project management.

## Ground Principles

- Follow a test-driven, test-first approach: define expected behavior with tests before implementing or changing behavior.
- Follow the configured quality tools and linters:
  - Backend (`backend/pyproject.toml`): `pytest`, `flake8`, `black`, `pre-commit`.
  - Frontend (`frontend/package.json`): `eslint`, `prettier` (and TypeScript tooling where applicable).
- Respect clean-code principles and maintain clear documentation of architecture and design decisions.
- Keep and respect the existing project structure:
  - `frontend/`: React web application frontend.
  - `backend/`: FastAPI-based Python backend.
  - `design/`: design documents for specific features.

## In-Code Documentation Guidelines

The current codebase already uses Python docstrings and selective TypeScript comments. Keep that style consistent and tighten it with the following rules.

- Document behavior, not syntax: explain intent, constraints, and non-obvious decisions rather than restating what code already says.
- Keep comments and docstrings short and factual; update or remove them when behavior changes.
- Prefer self-explanatory names and types first; add comments only where names and types are not enough.
- Remove stale debug comments and commented-out code unless there is a clear, temporary migration reason.

### Backend (Python/FastAPI)

- Use triple-double-quote docstrings (`"""..."""`) for public classes, methods, and functions with non-trivial behavior.
- Start docstrings with a concise one-line summary in imperative/present tense.
- For service/domain methods, include `Args`, `Returns`, and `Raises` when inputs, outputs, or failures are not obvious.
- Use inline `#` comments sparingly for rationale (for example, cache behavior, migration steps, or external API assumptions), not for line-by-line narration.
- Keep Alembic migration comments focused on schema/data transition intent and ordering.

### Frontend (React/TypeScript)

- Use JSDoc-style comments (`/** ... */`) for shared exported helpers and API utility functions where call contracts are important.
- Use short inline `//` comments only for non-obvious UI/state behavior (for example, index base, async loading intent, or UX constraints).
- Avoid file-header filename comments and other redundant comments that duplicate file names or obvious JSX/styling code.
- Prefer documenting component contracts through strong TypeScript types (`Props`, field types, callback signatures), then add comments only for edge cases.

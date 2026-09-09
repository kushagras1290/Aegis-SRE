from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "execute_shell(",
    "cluster-admin",
    "OPENAI_API_KEY=sk-",
    "KUBECONFIG=",
)
EXCLUDED_DIRS = frozenset(
    {
        ".git",
        "docs",
        ".venv",
        "venv",
        "node_modules",
        ".next",
        "dist",
        "build",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".egg-info",
    }
)


def main() -> None:
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or EXCLUDED_DIRS.intersection(path.parts)
            or any(part.endswith(".egg-info") for part in path.parts)
            or path.name == "static_verify.py"
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN:
            if token in text:
                violations.append(f"{path.relative_to(ROOT)}: {token}")

    if violations:
        joined = "\n".join(violations)
        raise SystemExit(f"static safety verification failed:\n{joined}")
    print("static safety verification passed")


if __name__ == "__main__":
    main()

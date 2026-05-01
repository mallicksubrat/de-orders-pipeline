from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
SKIP_SUFFIXES = {
    ".db",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".lock",
    ".parquet",
    ".png",
    ".pyc",
}

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|auth[_-]?token|client[_-]?secret|secret[_-]?key)\b"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{20,}"
    ),
    re.compile(
        r"(?i)\bpassword\b\s*[:=]\s*['\"]?"
        r"(?!replace-with|change-me|example|dummy|test)[^'\"\s]{8,}"
    ),
    re.compile(r"(?i)://[^:/\s]+:[^@/\s]+@"),
]

ALLOWLIST = {
    ".env.example:4",
    "docker-compose.yml:7",
    "docker-compose.yml:38",
}


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {character: value.count(character) for character in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def _is_placeholder(value: str) -> bool:
    normalized = value.lower()
    return any(
        marker in normalized
        for marker in ("replace-with", "change-me", "example", "dummy", "test")
    )


def _is_probably_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:1024]
    except OSError:
        return True
    return b"\0" in chunk


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if _is_probably_binary(path):
            continue
        yield path


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in _iter_files(root):
        relative = path.relative_to(root)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            location = f"{relative}:{line_number}"
            if location in ALLOWLIST:
                continue
            if _is_placeholder(line):
                continue
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings.append(f"{location}: matched secret-like pattern")
                continue
            for candidate in re.findall(r"\b[A-Za-z0-9_+/=-]{32,}\b", line):
                if _is_placeholder(candidate):
                    continue
                if _entropy(candidate) >= 4.5:
                    findings.append(f"{location}: high-entropy token candidate")
                    break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan repository text files for committed secrets."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    findings = scan(args.root.resolve())
    if findings:
        print("Secret scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

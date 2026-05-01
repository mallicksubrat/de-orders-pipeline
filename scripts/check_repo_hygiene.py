from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

README_FORBIDDEN_PATTERNS = {
    "emoji headers": re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]"),
    "Airflow design-ready wording": re.compile(r"Airflow\s*\(design-ready\)", re.I),
    "What I Learned section": re.compile(r"^##\s+What I Learned\b", re.I | re.M),
    "plain-text architecture chain": re.compile(r"source\s*->\s*extractor", re.I),
}


def _git_ls_files(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    failures: list[str] = []
    readme = README.read_text(encoding="utf-8")

    for label, pattern in README_FORBIDDEN_PATTERNS.items():
        if pattern.search(readme):
            failures.append(f"README contains forbidden content: {label}")

    if "```mermaid" not in readme:
        failures.append("README architecture section must include a Mermaid diagram.")

    tracked_secrets = _git_ls_files("secrets/*")
    if tracked_secrets:
        failures.append(f"secrets/ must not be tracked: {tracked_secrets}")

    if (ROOT / "secrets").exists():
        failures.append("secrets/ directory must not exist in the repository workspace.")

    if failures:
        print("Repository hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

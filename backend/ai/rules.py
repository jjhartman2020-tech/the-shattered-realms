"""Rule retrieval layer for AI-driven rulings."""

from pathlib import Path
from typing import List


class RuleLibrary:
    """Loads project documentation and retrieves likely-relevant rule excerpts."""

    def __init__(self, docs_root: str = "docs") -> None:
        self.docs_root = Path(docs_root)

    def _documents(self):
        if not self.docs_root.exists():
            return []
        return [
            path
            for path in self.docs_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}
        ]

    def retrieve(self, query: str, limit: int = 6) -> List[str]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        matches = []

        for path in self._documents():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            lower = text.lower()
            score = sum(lower.count(term) for term in terms)
            if score <= 0:
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            useful = []
            for line in lines:
                line_lower = line.lower()
                if any(term in line_lower for term in terms):
                    useful.append(line)
                if len(useful) >= 4:
                    break

            excerpt = "\n".join(useful)[:1800]
            matches.append((score, f"SOURCE: {path.as_posix()}\n{excerpt}"))

        matches.sort(key=lambda item: item[0], reverse=True)
        return [excerpt for _, excerpt in matches[:limit]]

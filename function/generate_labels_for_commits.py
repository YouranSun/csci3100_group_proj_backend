from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from Repository.diff import AtomicDiff, Hunk
import os
import re
import difflib
import hashlib

def categorize_atomic_diffs(
    diffs: List[AtomicDiff],
    split_messages: Optional[List[str]] = None,
    default_category: str = "chore",
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    msgs = split_messages if (split_messages and len(split_messages) == len(diffs)) else [None] * len(diffs)

    for d, msg in zip(diffs, msgs):
        scores: Dict[str, float] = defaultdict(float)
        reasons: List[str] = []
        labels: List[str] = []

        file_path = getattr(d, "file_path", "") or ""
        hunk: Hunk = getattr(d, "hunk", None)
        old_lines = (hunk.old_lines if hunk and hunk.old_lines else []) or []
        new_lines = (hunk.new_lines if hunk and hunk.new_lines else []) or []
        is_new = bool(getattr(d, "is_new_file", False))
        is_deleted = bool(getattr(d, "is_deleted_file", False))

        if msg:
            _apply_message_signals(msg, scores, reasons, labels)

        _apply_path_signals(file_path, scores, reasons)

        _apply_diff_signals(
            file_path=file_path,
            old_lines=old_lines,
            new_lines=new_lines,
            is_new=is_new,
            is_deleted=is_deleted,
            scores=scores,
            reasons=reasons,
            labels=labels,
        )

        category, confidence = _select_category(scores, default_category)

        scope = _infer_scope(file_path)

        if msg and _is_breaking_message(msg):
            labels.append("breaking_change")
            reasons.append("Breaking-change marker in message.")

        results.append({
            "signature": _signature_of_diff(d),
            "file": file_path,
            "scope": scope,
            "category": category,
            "confidence": round(confidence, 2),
            "labels": sorted(set(labels)),
            "reasons": reasons,
            "message": msg,
        })

    return results


def group_diffs_by_category(
    diffs: List[AtomicDiff],
    classifications: List[Dict[str, Any]],
) -> Dict[str, List[AtomicDiff]]:
    buckets: Dict[str, List[AtomicDiff]] = defaultdict(list)
    for d, c in zip(diffs, classifications):
        buckets[c["category"]].append(d)
    return dict(buckets)


TYPE_PREFIX_RE = re.compile(
    r"^\s*(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security|deps)"
    r"(?P<bang>!)?(?:\([^)]+\))?:",
    re.IGNORECASE,
)

MESSAGE_KEYWORDS: Dict[str, List[str]] = {
    "feat": ["feature", "add", "introduce", "support", "implement", "enable", "new"],
    "fix": ["fix", "bug", "issue", "defect", "patch", "correct", "resolve", "repair", "hotfix"],
    "docs": ["docs", "documentation", "readme", "changelog", "guide", "docstring"],
    "refactor": ["refactor", "cleanup", "restructure", "rename", "reorganize", "simplify"],
    "test": ["test", "tests", "unit test", "integration test", "e2e", "spec"],
    "perf": ["perf", "performance", "optimize", "latency", "throughput", "memory", "faster", "cache"],
    "build": ["build", "release", "artifact", "docker", "container", "packaging"],
    "ci": ["ci", "pipeline", "workflow", "actions", "travis", "circleci", "jenkins"],
    "style": ["format", "lint", "prettier", "clang-format", "black", "isort", "style", "whitespace", "typo"],
    "security": ["cve", "xss", "csrf", "rce", "ssrf", "injection", "sanitize", "escape", "auth", "permission", "jwt", "bcrypt", "encryption"],
    "deps": ["bump", "upgrade", "update dependency", "dependabot", "pin", "unpin", "requirements", "lockfile"],
    "revert": ["revert", "roll back", "rollback", "undo"],
}

def _apply_message_signals(msg: str, scores: Dict[str, float], reasons: List[str], labels: List[str]) -> None:
    m = TYPE_PREFIX_RE.match(msg)
    if m:
        t = m.group("type").lower()
        scores[t] += 4.0
        reasons.append(f"Message type prefix suggests '{t}'.")
        if m.group("bang"):
            labels.append("breaking_change")
    low = msg.lower()
    for cat, kws in MESSAGE_KEYWORDS.items():
        for kw in kws:
            if kw in low:
                scores[cat] += 1.2


def _is_breaking_message(msg: str) -> bool:
    low = msg.lower()
    return bool(TYPE_PREFIX_RE.match(msg) and "!" in msg.split(":", 1)[0]) or "breaking change" in low


PATH_CATEGORY_PATTERNS: List[Tuple[re.Pattern, str, float, str]] = [
    (re.compile(r"(^|/)(tests?|__tests__|specs?)(/|$)|(_test|\.spec)\.", re.I), "test", 3.0, "Path indicates tests."),
    (re.compile(r"(^|/)(docs?|documentation)(/|$)|readme(\.\w+)?$|changelog(\.\w+)?$", re.I), "docs", 3.0, "Path indicates docs."),
    (re.compile(r"(^|/)\.github/workflows/|(^|/)\.circleci/|travis\.yml$|gitlab-ci\.yml$|Jenkinsfile$", re.I), "ci", 3.0, "Path indicates CI."),
    (re.compile(r"Dockerfile$|docker-compose\.ya?ml$|^Makefile$|build\.gradle(\.kts)?$|pom\.xml$|CMakeLists\.txt$", re.I), "build", 2.5, "Build tooling file."),
    (re.compile(r"package\.json$|package-lock\.json$|yarn\.lock$|pnpm-lock\.yaml$|requirements\.txt$|Pipfile(\.lock)?$|poetry\.lock$|pyproject\.toml$|Cargo\.(toml|lock)$|go\.(mod|sum)$|Gemfile(\.lock)?$|composer\.(json|lock)$", re.I), "deps", 3.0, "Dependency manifest/lockfile."),
    (re.compile(r"(^|/)security(/|$)|(^|/)auth(entication)?(/|$)|crypto|certs?|keys?(/|$)", re.I), "security", 1.5, "Security-related path."),
    (re.compile(r"\.(md|rst|adoc|txt)$", re.I), "docs", 2.0, "Documentation file extension."),
    (re.compile(r"\.(json|yaml|yml|toml|ini|cfg|editorconfig|eslintrc.*|prettierrc.*)$", re.I), "chore", 1.0, "Configuration file."),
]

def _apply_path_signals(file_path: str, scores: Dict[str, float], reasons: List[str]) -> None:
    for pattern, cat, weight, why in PATH_CATEGORY_PATTERNS:
        if pattern.search(file_path):
            scores[cat] += weight
            reasons.append(why)


COMMENT_PREFIXES = {
    ".py": ["#", '"""', "'''"],
    ".js": ["//", "/*", "*", "*/"],
    ".ts": ["//", "/*", "*", "*/"],
    ".java": ["//", "/*", "*", "*/"],
    ".go": ["//", "/*", "*", "*/"],
    ".c": ["//", "/*", "*", "*/"],
    ".cpp": ["//", "/*", "*", "*/"],
    ".rb": ["#", "=begin", "=end"],
    ".rs": ["//", "/*", "*/"],
    ".sql": ["--"],
    ".sh": ["#"],
}

TEST_TOKENS = ["assert", "expect(", "describe(", "it(", "@Test", "pytest", "unittest", "should "]
DOC_TOKENS = ["# ", "///", "/**", "/*", "* ", "-- ", "docstring", "README"]
STYLE_TOKENS = ["fmt", "format", "lint", "disable-lint", "eslint-disable", "prettier-ignore", "black", "isort"]
PERF_TOKENS = ["cache", "memo", "optimiz", "fast", "latency", "O(", "vectori", "stream"]
SEC_TOKENS = ["sanitize", "escape", "encrypt", "decrypt", "bcrypt", "jwt", "rbac", "acl", "validate", "csrf", "xss", "injection"]
FIX_TOKENS = ["fix", "bug", "null", "exception", "error", "race", "deadlock", "off-by-one"]
RENAME_TOKENS = ["rename", "move", "reorganize"]

def _apply_diff_signals(
    file_path: str,
    old_lines: List[str],
    new_lines: List[str],
    is_new: bool,
    is_deleted: bool,
    scores: Dict[str, float],
    reasons: List[str],
    labels: List[str],
) -> None:
    ext = os.path.splitext(file_path)[1].lower()

    if is_new and not is_deleted:
        scores["feat"] += 0.8
        reasons.append("New file suggests feature addition.")
    if is_deleted and not is_new:
        scores["chore"] += 0.5
        reasons.append("File deletion suggests cleanup/chore.")

    if _is_whitespace_only_change(old_lines, new_lines):
        scores["style"] += 5.0
        reasons.append("Whitespace-only changes.")

    if _is_comment_or_docs_only_change(ext, old_lines, new_lines):
        scores["docs"] += 3.0
        reasons.append("Comment/docs-only change.")

    low_added = "\n".join(new_lines).lower()

    # Tokens
    if sum(1 for t in TEST_TOKENS if t in low_added) >= 1:
        scores["test"] += 1.2
    if any(t.lower() in low_added for t in DOC_TOKENS):
        scores["docs"] += 0.8
    if any(t in low_added for t in STYLE_TOKENS):
        scores["style"] += 0.8
    if any(t in low_added for t in PERF_TOKENS):
        scores["perf"] += 1.0
    if any(t in low_added for t in SEC_TOKENS):
        scores["security"] += 1.2
    if any(t in low_added for t in FIX_TOKENS):
        scores["fix"] += 1.0
    if any(t in low_added for t in RENAME_TOKENS):
        scores["refactor"] += 0.8

    # Similarity: likely refactor (non-behavioral)
    sim = _similarity_ratio("\n".join(old_lines), "\n".join(new_lines))
    if 0.85 <= sim < 0.98 and not _contains_behavioral_keywords(low_added):
        scores["refactor"] += 1.5
        reasons.append(f"High similarity ({sim:.2f}) suggests refactor.")

    # Manifests / CI / Build nudges
    if _looks_like_manifest(file_path):
        scores["deps"] += 1.5
        labels.append("dependency_update")
        reasons.append("Manifest/lockfile change.")
    if _looks_like_ci(file_path):
        scores["ci"] += 1.5
        reasons.append("CI workflow change.")
    if _looks_like_build(file_path):
        scores["build"] += 1.0
        reasons.append("Build tooling change.")


def _is_whitespace_only_change(old: List[str], new: List[str]) -> bool:
    strip = lambda s: re.sub(r"\s+", "", s or "")
    return strip("\n".join(old)) == strip("\n".join(new)) and (old or new)


def _is_comment_or_docs_only_change(ext: str, old: List[str], new: List[str]) -> bool:
    if ext in (".md", ".rst", ".adoc", ".txt"):
        return True
    prefixes = COMMENT_PREFIXES.get(ext, [])
    if not prefixes:
        return False
    def is_comment(line: str) -> bool:
        s = (line or "").lstrip()
        return any(s.startswith(p) for p in prefixes) or s == ""
    return all(is_comment(l) for l in old + new if l is not None)


def _similarity_ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(a=a, b=b).ratio()


def _contains_behavioral_keywords(low: str) -> bool:
    return any(k in low for k in ["add", "implement", "feature", "fix", "bug", "support", "new "])


def _looks_like_manifest(path: str) -> bool:
    return bool(re.search(r"(package\.json|requirements\.txt|Pipfile(\.lock)?|poetry\.lock|pyproject\.toml|Cargo\.(toml|lock)|go\.(mod|sum)|Gemfile(\.lock)?|composer\.(json|lock)|yarn\.lock|pnpm-lock\.yaml)$", path, re.I))


def _looks_like_ci(path: str) -> bool:
    return bool(re.search(r"(^|/)\.github/workflows/|(^|/)\.circleci/|travis\.yml$|gitlab-ci\.yml$|Jenkinsfile$", path, re.I))


def _looks_like_build(path: str) -> bool:
    return bool(re.search(r"Dockerfile$|docker-compose\.ya?ml$|^Makefile$|build\.gradle(\.kts)?$|pom\.xml$|CMakeLists\.txt$", path, re.I))


# Category selection, scope, signature

ALL_CATEGORIES = ["feat", "fix", "docs", "refactor", "test", "perf", "build", "ci", "chore", "style", "security", "deps", "revert"]

def _select_category(scores: Dict[str, float], default_category: str) -> Tuple[str, float]:
    if not scores:
        return default_category, 0.5
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    top_cat, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    # If the top score is very weak, prefer default to avoid noisy picks
    if top_score < 1.0 and default_category not in (top_cat,):
        top_cat = default_category
    margin = max(0.0, top_score - second_score)
    confidence = 0.5 + 0.5 * (margin / max(1.0, top_score))
    return top_cat, min(1.0, max(0.5, confidence))


SCOPE_ROOTS = ["src", "lib", "app", "cmd", "internal", "packages", "services", "server", "client", "components", "modules", "pkg"]

def _infer_scope(file_path: str) -> str:
    if not file_path:
        return "misc"
    parts = [p for p in file_path.split("/") if p]
    if not parts:
        return "misc"
    for root in SCOPE_ROOTS:
        if parts[0] == root and len(parts) > 1:
            return parts[1]
        if parts[0] in (".github",) and len(parts) > 1:
            return "ci"
    return parts[0] if len(parts) > 1 else os.path.splitext(parts[0])[0]


def _signature_of_diff(d: AtomicDiff) -> str:
    h = hashlib.sha1()
    file_path = getattr(d, "file_path", "") or ""
    is_new = str(getattr(d, "is_new_file", False))
    is_deleted = str(getattr(d, "is_deleted_file", False))
    hunk: Hunk = getattr(d, "hunk", None)
    old_lines = "\n".join(hunk.old_lines) if (hunk and hunk.old_lines) else ""
    new_lines = "\n".join(hunk.new_lines) if (hunk and hunk.new_lines) else ""
    h.update(file_path.encode("utf-8"))
    h.update(is_new.encode("utf-8"))
    h.update(is_deleted.encode("utf-8"))
    h.update(old_lines.encode("utf-8"))
    h.update(new_lines.encode("utf-8"))
    return h.hexdigest()
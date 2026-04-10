#!/usr/bin/env python3
"""A2A Ingestion Layer for Genesis Celestial Body schema."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".rs": "rust",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "react",
    ".jsx": "react",
    ".go": "go",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "shell",
}


def _safe_read(path: Path, max_chars: int = 5000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def _estimate_atmosphere(repo_name: str, readme_text: str) -> dict:
    source = f"{repo_name}\n{readme_text}".lower()
    novelty = 0.4
    if "experimental" in source or "prototype" in source:
        novelty += 0.25
    if "conscious" in source or "reasoning" in source:
        novelty += 0.2

    safety = 0.5
    if "security" in source or "zero-trust" in source:
        safety += 0.3
    if "sandbox" in source:
        safety += 0.15

    determinism = 0.35
    if "deterministic" in source or "verification" in source:
        determinism += 0.4
    if "attestation" in source:
        determinism += 0.2

    return {
        "intent_signature": "knowledge-ingestion",
        "novelty_index": round(min(novelty, 1.0), 3),
        "safety_index": round(min(safety, 1.0), 3),
        "determinism_index": round(min(determinism, 1.0), 3),
    }


def _estimate_gravity(total_files: int, loc: int, language_count: int) -> dict:
    compute_mass = round(min(1.0, 0.15 + (loc / 40000.0)), 3)
    influence = round(min(1.0, 0.1 + (total_files / 300.0) + (language_count / 20.0)), 3)
    orbit = "stable" if influence < 0.8 else "high-influence"
    return {
        "compute_mass": compute_mass,
        "influence_score": influence,
        "orbit_class": orbit,
    }


@dataclass
class CelestialBody:
    schema_version: str
    body_id: str
    source: dict
    mass: dict
    atmosphere: dict
    gravity: dict
    seismic: dict
    generated_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def ingest_repo_to_celestial_body(repo_path: str) -> dict:
    root = Path(repo_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid repository path: {repo_path}")

    files = [
        p for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
    ]
    total_files = len(files)

    lang_stats = {}
    line_count = 0
    hashed_material = []
    for file_path in files:
        ext = file_path.suffix.lower()
        lang = EXTENSION_LANGUAGE_MAP.get(ext, "other")
        lang_stats[lang] = lang_stats.get(lang, 0) + 1
        text = _safe_read(file_path)
        if text:
            line_count += text.count("\n") + 1
            hashed_material.append(f"{file_path.relative_to(root)}::{text[:200]}")

    readme = next((p for p in files if p.name.lower().startswith("readme")), None)
    readme_text = _safe_read(readme) if readme else ""

    identity_seed = "\n".join(sorted(hashed_material)[:200])
    body_id = hashlib.sha256(identity_seed.encode("utf-8")).hexdigest()[:16]

    atmosphere = _estimate_atmosphere(root.name, readme_text)
    gravity = _estimate_gravity(total_files, line_count, len(lang_stats))

    body = CelestialBody(
        schema_version="1.0.0",
        body_id=f"celestial-{body_id}",
        source={
            "type": "repository",
            "path": str(root),
            "name": root.name,
        },
        mass={
            "total_files": total_files,
            "estimated_loc": line_count,
            "language_distribution": dict(sorted(lang_stats.items())),
        },
        atmosphere=atmosphere,
        gravity=gravity,
        seismic={
            "citations_ready": True,
            "stress_test_status": "pending",
            "ingestion_invariant": "STRUCTURALLY_VERIFIABLE_CONSISTENCY",
        },
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    return body.to_dict()


def ingest_raw_code_to_celestial_body(name: str, code: str, language_hint: str = "unknown") -> dict:
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]
    loc = code.count("\n") + 1 if code else 0

    atmosphere = {
        "intent_signature": "raw-agent-ingest",
        "novelty_index": 0.55,
        "safety_index": 0.5,
        "determinism_index": 0.45,
    }
    gravity = _estimate_gravity(total_files=1, loc=loc, language_count=1)

    body = CelestialBody(
        schema_version="1.0.0",
        body_id=f"celestial-{digest}",
        source={"type": "raw_code", "name": name},
        mass={
            "total_files": 1,
            "estimated_loc": loc,
            "language_distribution": {language_hint: 1},
        },
        atmosphere=atmosphere,
        gravity=gravity,
        seismic={
            "citations_ready": False,
            "stress_test_status": "pending",
            "ingestion_invariant": "STRUCTURALLY_VERIFIABLE_CONSISTENCY",
        },
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    return body.to_dict()


if __name__ == "__main__":
    print(json.dumps(ingest_repo_to_celestial_body("."), indent=2))

"""Local filesystem StorageBackend implementation."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.models import RawDocument
from pipeline.storage.artifacts import StoredArtifact
from pipeline.storage.paths import raw_document_key


class LocalFilesystemBackend:
    """
    Writes under {data_dir}/ using ADR-001 key layout.

    Idempotent: writing an existing content_hash returns the existing artifact
    without modifying the file.
    """

    def __init__(self, data_dir: Path) -> None:
        self._root = data_dir.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def _path_for_key(self, key: str) -> Path:
        return self._root / Path(*key.split("/"))

    def write_raw_document(self, document: RawDocument) -> StoredArtifact:
        existing = self._find_raw_path(document.content_hash)
        if existing is not None:
            return StoredArtifact(
                key=self._key_from_path(existing),
                uri=existing.as_uri(),
                local_path=existing,
                created=False,
            )

        key = raw_document_key(document.content_hash, document.ingested_at)
        path = self._path_for_key(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = document.model_dump_json(indent=2)
        path.write_text(payload, encoding="utf-8")

        return StoredArtifact(
            key=key,
            uri=path.as_uri(),
            local_path=path,
            created=True,
        )

    def raw_document_exists(self, content_hash: str) -> bool:
        return self.read_raw_document(content_hash) is not None

    def _find_raw_path(self, content_hash: str) -> Path | None:
        raw_root = self._root / "raw"
        if not raw_root.is_dir():
            return None
        for date_dir in raw_root.iterdir():
            if not date_dir.is_dir():
                continue
            candidate = date_dir / f"{content_hash}.json"
            if candidate.is_file():
                return candidate
        return None

    @staticmethod
    def _key_from_path(path: Path) -> str:
        """Derive storage key from path under raw/{date}/{hash}.json."""
        date_part = path.parent.name
        return f"raw/{date_part}/{path.name}"

    def read_raw_document(self, content_hash: str) -> RawDocument | None:
        path = self._find_raw_path(content_hash)
        if path is None:
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return RawDocument.model_validate(data)

    def list_raw_keys(self) -> list[str]:
        """All raw object keys under root (testing helper)."""
        keys: list[str] = []
        raw_root = self._root / "raw"
        if not raw_root.is_dir():
            return keys
        for date_dir in sorted(raw_root.iterdir()):
            if not date_dir.is_dir():
                continue
            date_part = date_dir.name
            for file_path in date_dir.glob("*.json"):
                keys.append(f"raw/{date_part}/{file_path.name}")
        return keys


def build_local_storage(data_dir: Path) -> LocalFilesystemBackend:
    """Factory for local storage from resolved Settings.data_dir."""
    return LocalFilesystemBackend(data_dir)

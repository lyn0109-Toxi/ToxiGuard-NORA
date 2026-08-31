from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __project_schema_version__
from .evidence import DocumentRecord, EvidenceAssertion
from .models import AssessmentInput


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AuditEvent:
    event_id: str
    timestamp_utc: str
    action: str
    actor: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def create(cls, action: str, detail: str, actor: str = "현재 사용자") -> "AuditEvent":
        return cls(
            event_id=f"AUD-{uuid.uuid4().hex[:12]}",
            timestamp_utc=utc_now(),
            action=action,
            actor=actor or "현재 사용자",
            detail=detail,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AuditEvent":
        return cls(
            event_id=str(payload.get("event_id", "")),
            timestamp_utc=str(payload.get("timestamp_utc", "")),
            action=str(payload.get("action", "")),
            actor=str(payload.get("actor", "")),
            detail=str(payload.get("detail", "")),
        )


@dataclass
class ProjectBundle:
    project_id: str
    project_name: str
    created_at_utc: str
    updated_at_utc: str
    owner: str
    description: str
    assessment_input: AssessmentInput
    documents: list[DocumentRecord] = field(default_factory=list)
    assertions: list[EvidenceAssertion] = field(default_factory=list)
    audit_events: list[AuditEvent] = field(default_factory=list)
    last_result: dict[str, Any] | None = None

    @classmethod
    def new(cls, name: str = "새 EarlyTox 프로젝트", owner: str = "") -> "ProjectBundle":
        now = utc_now()
        return cls(
            project_id=f"PRJ-{uuid.uuid4().hex[:12]}",
            project_name=name,
            created_at_utc=now,
            updated_at_utc=now,
            owner=owner,
            description="",
            assessment_input=AssessmentInput(),
            audit_events=[AuditEvent.create("프로젝트 생성", name, owner or "현재 사용자")],
        )

    def touch(self) -> None:
        self.updated_at_utc = utc_now()

    def add_event(self, action: str, detail: str, actor: str | None = None) -> None:
        self.audit_events.append(AuditEvent.create(action, detail, actor or self.owner or "현재 사용자"))
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": __project_schema_version__,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "owner": self.owner,
            "description": self.description,
            "assessment_input": self.assessment_input.to_dict(),
            "documents": [item.to_dict() for item in self.documents],
            "assertions": [item.to_dict() for item in self.assertions],
            "audit_events": [item.to_dict() for item in self.audit_events],
            "last_result": self.last_result,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectBundle":
        return cls(
            project_id=str(payload.get("project_id") or f"PRJ-{uuid.uuid4().hex[:12]}"),
            project_name=str(payload.get("project_name", "EarlyTox 프로젝트")),
            created_at_utc=str(payload.get("created_at_utc", utc_now())),
            updated_at_utc=str(payload.get("updated_at_utc", utc_now())),
            owner=str(payload.get("owner", "")),
            description=str(payload.get("description", "")),
            assessment_input=AssessmentInput.from_dict(payload.get("assessment_input", {})),
            documents=[DocumentRecord.from_dict(item) for item in payload.get("documents", [])],
            assertions=[EvidenceAssertion.from_dict(item) for item in payload.get("assertions", [])],
            audit_events=[AuditEvent.from_dict(item) for item in payload.get("audit_events", [])],
            last_result=payload.get("last_result"),
        )


class ProjectStore:
    """Small local SQLite store for prototype project persistence.

    Streamlit Community Cloud filesystems may be ephemeral. The app therefore also
    supports explicit JSON export/import; SQLite is a convenience for local pilots.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        default_dir = Path(os.environ.get("NORA_DATA_DIR", Path.cwd() / ".nora_data"))
        default_dir.mkdir(parents=True, exist_ok=True)
        self.path = Path(path) if path else default_dir / "projects.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    owner TEXT,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, project: ProjectBundle) -> None:
        project.touch()
        payload = json.dumps(project.to_dict(), ensure_ascii=False)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO projects(project_id, project_name, owner, created_at_utc, updated_at_utc, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    project_name=excluded.project_name,
                    owner=excluded.owner,
                    updated_at_utc=excluded.updated_at_utc,
                    payload_json=excluded.payload_json
                """,
                (
                    project.project_id,
                    project.project_name,
                    project.owner,
                    project.created_at_utc,
                    project.updated_at_utc,
                    payload,
                ),
            )
            connection.commit()

    def load(self, project_id: str) -> ProjectBundle | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
        if not row:
            return None
        return ProjectBundle.from_dict(json.loads(row["payload_json"]))

    def delete(self, project_id: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            connection.commit()

    def list_projects(self) -> list[dict[str, str]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT project_id, project_name, owner, created_at_utc, updated_at_utc
                FROM projects
                ORDER BY updated_at_utc DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]


def project_json_bytes(project: ProjectBundle) -> bytes:
    return json.dumps(project.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")


def load_project_json(data: bytes) -> ProjectBundle:
    payload = json.loads(data.decode("utf-8-sig"))
    return ProjectBundle.from_dict(payload)

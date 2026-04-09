"""
TaskFlow API scenario assets: source files and directory layouts for ENG-DEMO.

This module contains only data constants (no logic) so that demo_scaffold.py
stays within the 250-LoC soft limit.
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Target repository source files
# ------------------------------------------------------------------

TASKFLOW_README = """\
# TaskFlow API

A task management REST API for small development teams.

## Business Context

TaskFlow enables development teams to manage work items across multiple projects.
It supports task creation, assignment, priority management, and progress tracking.
An EU deployment is planned; GDPR compliance is required from the first release.

## Target Users

- **Development team leads** – create and assign tasks, manage sprints
- **Team members** – update task status, log time, add comments
- **Project managers** – track progress, generate reports, manage budgets

## Functional Scope (v1.0)

1. Task CRUD with priority, due date, and label support
2. User authentication and role-based access control (admin / lead / member)
3. Project and sprint grouping
4. Activity audit log (append-only, immutable)
5. Webhook notifications for CI/CD pipeline integration

## Non-Functional Requirements

- API response time < 200 ms (p95) under 100 concurrent users
- 99.5 % uptime SLA (monthly, excluding planned maintenance windows)
- GDPR Article 17 (right to erasure): personal data pseudonymisation on request
- Data residency: EU-West (Frankfurt) primary, EU-North (Ireland) failover

## Technology Preferences

- Language: Python 3.12
- Web framework: FastAPI
- Database: PostgreSQL 16
- Authentication: JWT (RS256 signed)
- Deployment: Kubernetes on GKE (Google Kubernetes Engine)

## Out of Scope for v1.0

- Mobile applications (planned v1.5)
- Real-time collaboration (planned v2.0)
- AI-powered task suggestions (future)
"""

TASKFLOW_REQUIREMENTS = """\
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
asyncpg==0.29.0
alembic==1.13.3
pydantic==2.9.2
pydantic-settings==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.2
"""

TASKFLOW_MAIN = '''\
"""TaskFlow API — application entry point."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow API",
    version="0.1.0",
    description="Task management REST API for development teams.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
'''

TASKFLOW_MODELS = '''\
"""Domain models — SQLAlchemy ORM entities."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum as SAEnum, ForeignKey, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Set on GDPR Article 17 erasure; email replaced with pseudonym
    pseudonymised_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority), nullable=False, default=Priority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), nullable=False, default=TaskStatus.BACKLOG
    )
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    project: Mapped["Project | None"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["User | None"] = relationship("User", back_populates="tasks")
'''

GITIGNORE = """\
__pycache__/
*.py[cod]
.env
.venv/
*.egg-info/
dist/
.pytest_cache/
"""

# ------------------------------------------------------------------
# Directory layout constants
# ------------------------------------------------------------------

WORK_REPO_DIRS: list[str] = [
    "architecture-repository/model-entities/motivation/stakeholders",
    "architecture-repository/model-entities/motivation/drivers",
    "architecture-repository/model-entities/motivation/goals",
    "architecture-repository/model-entities/motivation/requirements",
    "architecture-repository/model-entities/motivation/constraints",
    "architecture-repository/model-entities/motivation/principles",
    "architecture-repository/model-entities/strategy/capabilities",
    "architecture-repository/model-entities/strategy/value-streams",
    "architecture-repository/model-entities/business/actors",
    "architecture-repository/model-entities/business/roles",
    "architecture-repository/model-entities/business/processes",
    "architecture-repository/model-entities/business/services",
    "architecture-repository/model-entities/application/components",
    "architecture-repository/model-entities/application/services",
    "architecture-repository/model-entities/application/interfaces",
    "architecture-repository/model-entities/application/data-objects",
    "architecture-repository/model-entities/implementation",
    "architecture-repository/connections/archimate/association",
    "architecture-repository/connections/archimate/composition",
    "architecture-repository/connections/archimate/realization",
    "architecture-repository/connections/archimate/serving",
    "architecture-repository/diagram-catalog/diagrams",
    "architecture-repository/diagram-catalog/rendered",
    "architecture-repository/decisions",
    "architecture-repository/overview",
    "technology-repository",
    "project-repository",
    "safety-repository",
    "delivery-repository",
    "qa-repository",
    "devops-repository",
]

ENGAGEMENT_DIRS: list[str] = [
    "clarification-log",
    "algedonic-log",
    "handoff-log",
    "workflow-events",
]

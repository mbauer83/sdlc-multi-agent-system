# General Python Coding Guidelines

All Python implementation (`src/`) must follow these conventions. They apply to every file authored in Stage 5 onward and are enforced during code review.

## Type system - expressive and mandatory

- Type annotations are required on all function and method signatures (parameters and return types). No bare `def f(x)` without annotations.
- Modern syntax for built-in collection types (PEP 585/604): write `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[T]`, `type[X]` directly - never the capitalized `typing` aliases `List`, `Dict`, `Tuple`, `Set`, `FrozenSet`, `Type`. Use `X | Y` instead of `Union[X, Y]`, and `X | None` instead of `Optional[X]`.
- Parametric polymorphism - prefer inline type parameter syntax (PEP 695, Python 3.12+): write `def f[T](x: T) -> T` and `class Stack[T]: ...` instead of declaring `T = TypeVar('T')` separately. Bounds and constraints are written inline - `[T: SomeBase]` for an upper bound, `[T: (int, float)]` for constraints. Use `[**P]` for a `ParamSpec` parameter and `[*Ts]` for a `TypeVarTuple`. Explicit `TypeVar` declarations are still required only when variance must be stated explicitly (covariant/contravariant) and cannot be inferred by the type checker - this is an edge case; prefer letting inference handle it. Use the `type` statement (PEP 695) for named type aliases: `type Vector = list[float]` - not `TypeAlias` from `typing`.
- `Protocol` (from `typing`) is still required for structural subtyping - preferred over `ABC` for interface definitions. `overload` (from `typing`) is still required for multi-dispatch signatures. These have no PEP 695 equivalents.
- Use `TypedDict` or Pydantic `BaseModel` for structured data; never `dict[str, Any]` at a boundary.

## Pythonic style - current best practices

- Prefer compositional, functional style over imperative mutation: use comprehensions, `map`/`filter` where readable, generator expressions, and `functools` where appropriate.
- Use `dataclasses` (with `slots=True` where applicable) for lightweight value objects that do not need Pydantic validation.
- Use `match`/`case` (structural pattern matching, PEP 634) for multi-branch dispatch on tagged unions or event types - preferred over long `if/elif` chains.
- Use `pathlib.Path` throughout; never `os.path` string concatenation.
- Use f-strings for all string formatting; never `%` formatting or `.format()`.

## Error handling - monadic, no exceptions for control flow

- Use Result-style returns via a lightweight `Result[T, E]` type (either a project-local definition or `returns` library) for operations that can fail in expected ways. Do not raise exceptions for expected failure paths (missing artifact, validation failure, CQ not found).
- Raise exceptions only for truly unexpected states (programming errors, unrecoverable I/O failures). Use `assert` only for internal invariants, never for user-facing validation.
- Avoid bare `except Exception` clauses. If catching broadly, re-raise or log with full context.
- Pydantic `ValidationError` is acceptable at system boundaries (external input validation); never swallow it silently.

## No magic

- No monkey-patching, no `__getattr__` tricks, no dynamic `setattr` unless implementing a clearly bounded, well-documented protocol (for example, Pydantic internals).
- No `globals()` / `locals()` manipulation.
- Dependency injection over module-level singletons; pass configuration and dependencies explicitly.

## Domain-centred architecture - layered dependency rule

The codebase follows a domain-centred layered architecture (hexagonal / ports-and-adapters style). The dependency rule is strict: outer layers depend inward; the domain depends on nothing outside itself.

```
┌─────────────────────────────────────────────┐
│  Infrastructure  (src/events/, src/sources/) │  ← depends on Application + Domain + Common
├─────────────────────────────────────────────┤
│  Application     (src/agents/, src/orch.)   │  ← depends on Domain + Common
├─────────────────────────────────────────────┤
│  Domain          (src/models/, src/domain/) │  ← depends on Common only
├─────────────────────────────────────────────┤
│  Common          (src/common/)              │  ← no business or framework dependencies;
│  logging, validation, parsing, normalisation│    usable by all layers
└─────────────────────────────────────────────┘
```

Cross-cutting concerns that are genuinely needed at every layer - logging, structured validation helpers, text parsing utilities, normalisation functions - live in `src/common/`. This module has no business-domain knowledge and no infrastructure dependencies; it is pure utility. All layers may import from `src/common/` without violating the dependency rule. What is prohibited is importing inward across the business layers (infrastructure importing application logic, application importing infrastructure implementations) or importing framework-specific types into the domain.

- Domain layer (`src/models/`, `src/domain/`): Pydantic models, value objects, domain events, aggregate roots, domain services. May import from `src/common/` (for example, logging, shared validators). No imports from PydanticAI, SQLAlchemy, LangGraph, Anthropic SDK, `pathlib` I/O, or any framework. Domain logic (validation rules, state transitions, constraint checks) lives here and is fully unit-testable without mocking.
- Application layer (`src/agents/`, `src/orchestration/`): orchestrates domain objects; invokes infrastructure via ports (abstract `Protocol` interfaces defined in the domain or application layer). Depends on the domain; never directly on infrastructure implementations. Agent skill execution, handoff routing, and CQ lifecycle management live here.
- Infrastructure layer (`src/events/`, `src/sources/`, future `src/dashboard/`): implements the ports - EventStore (SQLite), source adapters (Confluence, Jira, Git), file-system artifact I/O, plantuml CLI subprocess. Infrastructure knows about domain types (it uses them as data shapes) but domain types never know about infrastructure.

## Ports and adapters pattern for all I/O

- Define a `Protocol` (port) in the application or domain layer for every infrastructure capability needed: `ArtifactReader`, `ArtifactWriter`, `EventStore`, `LLMClient`, `SourceAdapter`.
- Concrete implementations (adapters) live in the infrastructure layer and are injected at composition root (startup / agent factory).
- This means the entire application and domain can be tested with in-memory fakes implementing the same protocols - no SQLite, no file system, no LLM API calls required.

## Domain representations are the single source of truth

- Pydantic models in `src/models/` are the canonical representation of SDLC artifacts (ArchitectureVision, BusinessArchitecture, LearningEntry, etc.). No parallel dict-based or ORM-mapped representations of the same concepts.
- EventStore events are also Pydantic models; the SQLite schema is derived from them (via Alembic), not defined independently.
- If a framework (PydanticAI, LangGraph) requires its own data shape, adapt at the boundary - wrap or map from the domain model; do not let framework types leak into domain or application code.

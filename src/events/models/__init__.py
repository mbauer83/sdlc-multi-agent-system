# Import all model modules to trigger EventRegistry.register() calls.
# Imported by src/events/__init__.py.
from . import (  # noqa: F401
    phase, cycle, gate, sprint, artifact, handoff,
    cq, algedonic, source,
    specialist, decision, review,
)

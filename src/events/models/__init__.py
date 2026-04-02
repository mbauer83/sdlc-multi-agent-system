# Import all model modules to trigger EventRegistry.register() calls.
# Imported by src/events/__init__.py.
from . import phase, cycle, gate, sprint, artifact, handoff, cq, algedonic, source  # noqa: F401

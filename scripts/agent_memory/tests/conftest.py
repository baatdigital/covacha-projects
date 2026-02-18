"""conftest.py — agrega scripts/agent_memory al sys.path para tests."""
import sys
import os

# Permite importar módulos de scripts/agent_memory directamente (ej: from bootstrap import ...)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

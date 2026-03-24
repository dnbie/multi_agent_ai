"""
Feature Manager - Central registry for all agent modules.
Checks if a feature/module exists before creating a new one.
Follows the REUSE-FIRST principle for BSc final year project.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feature_registry.json")


class FeatureManager:
    """
    Maintains a module registry.
    Before any new module is created the system checks this registry.
    - If module exists  -> return existing instance
    - If not           -> register and return a new one
    """

    _instance = None  # singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Any] = {}
        self._load_registry()

    # ── persistence ───────────────────────────────────────────────────────────

    def _load_registry(self):
        """Load saved registry from disk."""
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    self._registry = json.load(f)
            except Exception:
                self._registry = {}

    def _save_registry(self):
        """Persist registry to disk."""
        try:
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(self._registry, f, indent=2)
        except Exception:
            pass

    # ── public API ────────────────────────────────────────────────────────────

    def register(self, feature_name: str, module_path: str, capabilities: List[str],
                 description: str = "", instance: Any = None) -> Dict:
        """
        Register a module in the registry.
        If it already exists the existing entry is returned unchanged.
        """
        key = feature_name.lower().strip()
        if key in self._registry:
            return {"status": "already_exists", "entry": self._registry[key]}

        entry = {
            "name": feature_name,
            "module_path": module_path,
            "capabilities": capabilities,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
        }
        self._registry[key] = entry
        if instance is not None:
            self._instances[key] = instance
        self._save_registry()
        return {"status": "registered", "entry": entry}

    def exists(self, feature_name: str) -> bool:
        """Return True if the feature is already registered."""
        return feature_name.lower().strip() in self._registry

    def get(self, feature_name: str) -> Optional[Dict]:
        """Return registry entry or None."""
        return self._registry.get(feature_name.lower().strip())

    def get_instance(self, feature_name: str) -> Optional[Any]:
        """Return cached agent instance or None."""
        return self._instances.get(feature_name.lower().strip())

    def set_instance(self, feature_name: str, instance: Any):
        """Cache a live agent instance."""
        self._instances[feature_name.lower().strip()] = instance

    def list_all(self) -> List[Dict]:
        """Return all registered features."""
        return list(self._registry.values())

    def get_or_create(self, feature_name: str, factory_fn: callable,
                      module_path: str, capabilities: List[str],
                      description: str = "") -> Any:
        """
        Core REUSE-FIRST helper:
        - If instance already cached  -> return it
        - If registered but not cached -> call factory_fn(), cache and return
        - If not registered            -> register, call factory_fn(), cache and return
        """
        key = feature_name.lower().strip()
        if key in self._instances:
            return self._instances[key]

        instance = factory_fn()
        self._instances[key] = instance

        if key not in self._registry:
            self.register(feature_name, module_path, capabilities, description, instance)

        return instance

    def deactivate(self, feature_name: str):
        """Mark a feature as inactive."""
        key = feature_name.lower().strip()
        if key in self._registry:
            self._registry[key]["status"] = "inactive"
            self._save_registry()

    def summary(self) -> str:
        """Human-readable registry summary."""
        if not self._registry:
            return "No features registered yet."
        lines = [f"Feature Registry ({len(self._registry)} modules):"]
        for entry in self._registry.values():
            status = entry.get("status", "?")
            caps = ", ".join(entry.get("capabilities", [])[:2])
            lines.append(f"  [{status.upper()}] {entry['name']} — {caps}")
        return "\n".join(lines)

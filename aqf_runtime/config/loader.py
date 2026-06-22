from __future__ import annotations
import json
from pathlib import Path
from copy import deepcopy

DEFAULT_CONFIG_PATH = Path(__file__).with_name("default_config.json")

def load_config(config_path=None):
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as fp:
            return json.load(fp)
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)

def merge_config(base: dict, override: dict | None):
    if not override:
        return deepcopy(base)

    def _merge(a, b):
        out = deepcopy(a)
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = _merge(out[k], v)
            else:
                out[k] = v
        return out

    return _merge(base, override)

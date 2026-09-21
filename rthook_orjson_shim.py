"""
Runtime hook: Replace orjson with a robust stdlib-json shim for Windows 7 compatibility.
orjson is a Rust-based JSON library that uses Windows 8+ APIs (WaitOnAddress).
This shim provides the same interface using Python's built-in json module.
"""
import sys
import types
import json as _json

# ── Ensure nicegui.version is always hardcoded and never fails in frozen env ──
_ver_mod = types.ModuleType("nicegui.version")
_ver_mod.__version__ = "1.4.33"
sys.modules["nicegui.version"] = _ver_mod

_orjson = types.ModuleType("orjson")
_orjson.__file__ = __file__
_orjson.__loader__ = None
_orjson.__package__ = "orjson"
_orjson.__path__ = []

# ── Option flags (matching orjson's constants) ──
_orjson.OPT_SERIALIZE_NUMPY = 1 << 1
_orjson.OPT_NON_STR_KEYS = 1 << 6
_orjson.OPT_SORT_KEYS = 1 << 2
_orjson.OPT_INDENT_2 = 1 << 3
_orjson.OPT_APPEND_NEWLINE = 1 << 4
_orjson.OPT_NAIVE_UTC = 1 << 5
_orjson.OPT_UTC_Z = 1 << 7
_orjson.OPT_OMIT_MICROSECONDS = 1 << 8
_orjson.OPT_SERIALIZE_DATACLASS = 1 << 9
_orjson.OPT_SERIALIZE_UUID = 1 << 10
_orjson.OPT_PASSTHROUGH_DATETIME = 1 << 11
_orjson.OPT_PASSTHROUGH_SUBCLASS = 1 << 12
_orjson.OPT_STRICT_INTEGER = 1 << 13
_orjson.OPT_PASSTHROUGH_DATACLASS = 1 << 14

# ── JSONDecodeError / JSONEncodeError ──
_orjson.JSONDecodeError = _json.JSONDecodeError

class _JSONEncodeError(TypeError):
    pass

_orjson.JSONEncodeError = _JSONEncodeError


def _dumps(obj, default=None, option=None):
    """Return bytes, matching orjson.dumps signature, never throwing on custom objects."""
    def _default_handler(o):
        # If a custom default was provided, try it first
        if default is not None:
            try:
                res = default(o)
                return res
            except Exception:
                pass

        # Handle NumPy
        try:
            import numpy as np
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, np.bool_):
                return bool(o)
        except Exception:
            pass

        # Handle Dates & Times
        import datetime
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, datetime.time):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()

        # Handle UUID & Decimal
        try:
            import uuid
            if isinstance(o, uuid.UUID):
                return str(o)
        except Exception:
            pass

        from decimal import Decimal
        if isinstance(o, Decimal):
            return float(o)

        # Handle sets & bytes
        if isinstance(o, bytes):
            return o.decode("utf-8", errors="replace")
        if isinstance(o, (set, frozenset)):
            return list(o)

        # Handle dataclass or objects with __dict__
        if hasattr(o, '__dict__'):
            return o.__dict__

        # Fallback to string representation rather than crashing
        return str(o)

    kw = {
        "default": _default_handler,
        "ensure_ascii": False,
        "separators": (",", ":")
    }

    if option and (option & 4):  # OPT_SORT_KEYS
        kw["sort_keys"] = True
    if option and (option & 8):  # OPT_INDENT_2
        kw["indent"] = 2

    try:
        result = _json.dumps(obj, **kw)
    except Exception:
        # Extreme fallback
        result = _json.dumps(str(obj))

    return result.encode("utf-8")


def _loads(data):
    """Accept bytes or str, matching orjson.loads signature."""
    if isinstance(data, (bytes, bytearray, memoryview)):
        data = bytes(data).decode("utf-8")
    return _json.loads(data)


_orjson.dumps = _dumps
_orjson.loads = _loads
_orjson.Fragment = bytes

sys.modules["orjson"] = _orjson


# ── Fix Starlette StaticFiles Path vs str bug on Windows ─────────────────────
try:
    import os as _os
    import starlette.staticfiles

    def _fixed_lookup_path(self, path: str):
        for directory in self.all_directories:
            dir_str = _os.path.abspath(str(directory))
            joined_path = _os.path.join(dir_str, path)
            if self.follow_symlink:
                full_path = _os.path.abspath(joined_path)
            else:
                full_path = _os.path.realpath(joined_path)
                dir_str = _os.path.realpath(dir_str)
            try:
                if _os.path.commonpath([full_path, dir_str]) != dir_str:
                    continue
                return full_path, _os.stat(full_path)
            except (FileNotFoundError, NotADirectoryError, ValueError, OSError):
                continue
        return "", None

    starlette.staticfiles.StaticFiles.lookup_path = _fixed_lookup_path
except Exception:
    pass


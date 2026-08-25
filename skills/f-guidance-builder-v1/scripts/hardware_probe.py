#!/usr/bin/env python3
"""Print a privacy-safe local experiment hardware and accelerator profile as JSON."""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys


def memory_bytes() -> int | None:
    if sys.platform == "darwin":
        try:
            return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
        except (ValueError, OSError, AttributeError):
            return None
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return int(pages * page_size)
    except (ValueError, OSError, AttributeError):
        return None


def torch_profile() -> dict[str, object]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"installed": False, "import_error": type(exc).__name__}

    mps_backend = getattr(torch.backends, "mps", None)
    mps_available = bool(mps_backend and mps_backend.is_available())
    cuda_available = bool(torch.cuda.is_available())
    return {
        "installed": True,
        "version": torch.__version__,
        "mps_available": mps_available,
        "cuda_available": cuda_available,
        "cuda_device_count": torch.cuda.device_count() if cuda_available else 0,
        "recommended_device": "mps" if mps_available else "cuda" if cuda_available else "cpu",
    }


def main() -> int:
    disk = shutil.disk_usage(os.getcwd())
    profile = {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "conda_environment": os.environ.get("CONDA_DEFAULT_ENV"),
        "cpu_count": os.cpu_count(),
        "memory_bytes": memory_bytes(),
        "working_directory_disk_free_bytes": disk.free,
        "torch": torch_profile(),
        "privacy_note": "Serial numbers, UUIDs, usernames, hostnames, and network identifiers are intentionally omitted.",
    }
    print(json.dumps(profile, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Optional private PyTorch installation. Importing this module never imports Torch."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

PACKAGES = {"torch": "2.14.1", "sympy": "1.14.0", "networkx": "3.6.1", "mpmath": "1.3.0"}
PIP_WHEEL = "pip-23.2.1-py3-none-any.whl"
PIP_SHA256 = "7ccf472345f20d35bdc9d1841ff5f313260c2c33fe417f48c30ac46cccabf5be"
SOURCE = "https://pypi.org/project/torch/2.14.1/"
LICENSE_URL = "https://github.com/pytorch/pytorch/blob/v2.14.1/LICENSE"


def active_directory(root):
    base = (Path(root) / "runtime/components/pytorch").resolve()
    try:
        value = json.loads((base / "active.json").read_text("utf-8"))
        target = (base / value["directory"]).resolve()
        if value.get("schemaVersion") != 1 or not target.is_relative_to(base) or not (target / "torch/__init__.py").is_file():
            return None
        return target
    except (OSError, ValueError, KeyError, TypeError):
        return None


def activate(root):
    target = active_directory(root)
    if target is not None and str(target) not in sys.path:
        sys.path.insert(0, str(target))
    return target


def status(root):
    active = activate(root)
    packages = []
    for name, expected in PACKAGES.items():
        try:
            distribution = importlib.metadata.distribution(name)
            version = distribution.version
            present = (Path(distribution.locate_file(name)) / "__init__.py").is_file()
        except importlib.metadata.PackageNotFoundError:
            version, present = "", False
        packages.append({"name": name, "expectedVersion": expected, "version": version,
                         "installed": present and version.split("+")[0] == expected})
    ready = all(p["installed"] for p in packages)
    return {"component": "pytorch", "state": "Installed" if ready else "Missing",
            "ready": ready, "expectedVersion": PACKAGES["torch"], "version": packages[0]["version"],
            "packages": packages, "path": str(active or ""), "source": SOURCE,
            "license": "BSD-3-Clause", "licenseUrl": LICENSE_URL,
            "probeVerified": bool(ready and active)}


def install(root, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    base = (root / "runtime/components/pytorch").resolve()
    if sys.platform != "win32" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("The guided PyTorch installer supports Windows CPython 3.11 only.")
    if not destination.is_relative_to(base) or destination == base or destination.exists():
        raise ValueError("Expected a new private component directory.")
    wheel = root / "app/packages" / PIP_WHEEL
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != PIP_SHA256:
        raise RuntimeError("The bundled installer wheel failed SHA256 verification.")
    destination.mkdir(parents=True)
    args = ["install", "--isolated", "--keyring-provider", "disabled", "--disable-pip-version-check",
            "--index-url", "https://pypi.org/simple", "--only-binary=:all:", "--no-deps", "--no-compile",
            "--target", str(destination), *[name + "==" + version for name, version in PACKAGES.items()]]
    bootstrap = "import sys;sys.path.insert(0," + repr(str(wheel)) + ");from pip._internal.cli.main import main;raise SystemExit(main(" + repr(args) + "))"
    subprocess.run([sys.executable, "-c", bootstrap], stdout=sys.stderr, stderr=sys.stderr, check=True,
                   creationflags=0x08000000 if os.name == "nt" else 0)
    # Generated command launchers are not needed; inference uses this interpreter.
    entrypoints = destination / "bin"
    if entrypoints.is_dir():
        for entry in entrypoints.iterdir():
            if not entry.is_file():
                raise RuntimeError("Unexpected installer entry-point directory.")
            entry.unlink()
        entrypoints.rmdir()
    probe = "import sys,json;sys.path.insert(0," + repr(str(destination)) + ");import torch;assert torch.__version__.split('+')[0]=='" + PACKAGES["torch"] + "';assert torch.version.cuda is None;print(json.dumps({'cpu':True,'version':torch.__version__}))"
    result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True,
                            creationflags=0x08000000 if os.name == "nt" else 0)
    verified = json.loads(result.stdout)
    if verified.get("cpu") is not True:
        raise RuntimeError("CPU runtime verification failed.")
    marker = {"schemaVersion": 1, "directory": destination.relative_to(base).as_posix(),
              "version": PACKAGES["torch"], "cpu": True}
    temporary = base / ("active-" + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    temporary.replace(base / "active.json")
    # Status is resolved in a fresh worker; no already imported engine is replaced.
    return status(root)

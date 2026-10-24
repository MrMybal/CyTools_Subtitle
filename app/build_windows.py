"""Build a clean Windows x64 portable runtime; never copy the developer venv."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PYTHON_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
PYTHON_SHA256 = "009d6bf7e3b2ddca3d784fa09f90fe54336d5b60f0e0f305c37f400bf83cfd3b"
IGNORE = {"__pycache__", ".pytest_cache"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--directory", type=Path)
    args = parser.parse_args()
    version = json.loads((ROOT / "app/CyTool.json").read_text("utf-8"))["version"]
    name = f"CyTools_Subtitle-{version}-windows-x64"
    stage = (args.directory or ROOT / "runtime/portable-build" / name).resolve()
    if not args.package_only:
        if sys.platform != "win32" or sys.version_info[:2] != (3, 11) or sys.maxsize <= 2**32:
            raise SystemExit("Build with 64-bit CPython 3.11 on Windows.")
        if stage.exists():
            raise SystemExit("Build directory already exists; use a new directory or --package-only.")
        stage.mkdir(parents=True)
        cache = ROOT / "runtime/windows-downloads"
        cache.mkdir(parents=True, exist_ok=True)
        archive = cache / "python-3.11.9-embed-amd64.zip"
        if not archive.exists():
            with urllib.request.urlopen(PYTHON_URL, timeout=60) as source, archive.open("wb") as dest:
                shutil.copyfileobj(source, dest)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != PYTHON_SHA256:
            raise SystemExit("Python archive SHA256 mismatch.")
        scripts = stage / "runtime/python/Scripts"
        scripts.mkdir(parents=True)
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                target = (scripts / member.filename).resolve()
                if not target.is_relative_to(scripts.resolve()):
                    raise SystemExit("Unsafe Python archive path.")
            bundle.extractall(scripts)
        (scripts / "python311._pth").write_text(
            "python311.zip\n.\n../Lib/site-packages\n../../../app\nimport site\n", encoding="ascii")
        site = stage / "runtime/python/Lib/site-packages"
        (scripts / "sitecustomize.py").write_text(
            "import site, sys\nfrom pathlib import Path\n"
            "sys.dont_write_bytecode = True\n"
            "site.addsitedir(str(Path(__file__).resolve().parent.parent / 'Lib/site-packages'))\n",
            encoding="utf-8")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--keyring-provider", "disabled",
            "--disable-pip-version-check", "--only-binary=:all:", "--no-compile", "--no-deps",
            "--target", str(site), "--find-links", str(ROOT / "app/packages"),
            "--constraint", str(ROOT / "app/windows-constraints.txt"),
            "--requirement", str(ROOT / "app/requirements-base-windows.txt"),
        ], check=True)
        # pip entry-point launchers encode the build interpreter's absolute path.
        # The application invokes modules through its own interpreter instead.
        entrypoints = site / "bin"
        if entrypoints.is_dir():
            for item in entrypoints.iterdir():
                if not item.is_file():
                    raise RuntimeError("Unexpected directory in generated entry points.")
                item.unlink()
            entrypoints.rmdir()
        for info in site.glob("*.dist-info/direct_url.json"):
            info.unlink()
        # Modified upstream test setup: callers supply their own authentication.
        testing = site / "transformers/testing_utils.py"
        if testing.exists():
            import base64, csv, io, re
            text = testing.read_text("utf-8")
            text, count = re.subn(r'^TOKEN = [^\n]+$',
                'TOKEN = ""  # Modified by CyTools_Subtitle: tests supply their own authentication.',
                text, count=1, flags=re.MULTILINE)
            if count != 1:
                raise RuntimeError("Unexpected Transformers test configuration.")
            testing.write_text(text, encoding="utf-8")
            for record in site.glob("transformers-*.dist-info/RECORD"):
                rows = list(csv.reader(io.StringIO(record.read_text("utf-8"))))
                content = testing.read_bytes()
                digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode("ascii")
                for row in rows:
                    if row[0] == "transformers/testing_utils.py":
                        row[1:] = ["sha256=" + digest, str(len(content))]
                stream = io.StringIO(newline="")
                csv.writer(stream).writerows(rows)
                record.write_text(stream.getvalue(), encoding="utf-8", newline="")
        for source in (ROOT / "app").rglob("*"):
            if source.is_file() and not any(p in IGNORE for p in source.parts):
                dest = stage / source.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        for relative in ("CyTools_Subtitle.exe", "README.md", "LISEZ-MOI.md", "LICENSE"):
            shutil.copyfile(ROOT / relative, stage / relative)
        shutil.copytree(ROOT / "LICENCES", stage / "LICENCES")
        shutil.copyfile(scripts / "LICENSE.txt", stage / "LICENCES/Python-LICENSE.txt")
        (stage / "PORTABLE.txt").write_text(
            "CyTools_Subtitle " + version + " - Windows x64\n\n"
            "Extract the entire archive to a writable folder, then open CyTools_Subtitle.exe.\n"
            "Python and the media/UI runtime are included; no system Python is required.\n"
            "In Installation, download PyTorch, then review the model license and download Phonon-2 (English)\n"
            "or Phonon-2.5 (multilingual). PyTorch and model downloads require an internet connection.\n"
            "Keep app/ and runtime/ next to the executable. Settings and results are stored in data/.\n"
            "The application is AGPL-3.0-only. Component and model licenses are separate.\n", encoding="utf-8")
        (stage / "runtime/portable.json").write_text(json.dumps({
            "format": "cytools-portable-runtime", "schemaVersion": 1,
            "python": "3.11.9", "pythonSource": PYTHON_URL, "pythonSha256": PYTHON_SHA256,
            "platform": "windows-x64", "applicationVersion": version,
            "modelWeightsIncluded": False, "pytorchIncluded": False,
        }, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"state": "Built", "directory": str(stage)}), flush=True)
    if not (stage / "runtime/python/Scripts/python.exe").is_file():
        raise SystemExit("Portable interpreter missing.")
    if not args.package_only:
        print("Validate and relocate this directory, then run --package-only --directory PATH.")
        return
    out = ROOT / "runtime/distributions"
    out.mkdir(parents=True, exist_ok=True)
    target = out / (name + ".zip")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for source in sorted(stage.rglob("*")):
            relative = source.relative_to(stage)
            if relative.parts[0] == "runtime" and not (len(relative.parts) > 1 and (relative.parts[1] == "python" or relative.as_posix() == "runtime/portable.json")):
                continue
            if not source.is_file() or relative.parts[0] == "data" or any(p in IGNORE for p in relative.parts):
                continue
            bundle.write(source, name + "/" + relative.as_posix())
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    target.with_suffix(".zip.sha256").write_text(digest + "  " + target.name + "\n", encoding="ascii")
    print(json.dumps({"file": str(target), "bytes": target.stat().st_size, "sha256": digest}))


if __name__ == "__main__":
    main()

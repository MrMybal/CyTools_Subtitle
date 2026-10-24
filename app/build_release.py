"""Package sources/app updates, excluding private data, models and environments."""
from pathlib import Path
import hashlib
import json
import stat
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"runtime/distributions"
OUT.mkdir(parents=True,exist_ok=True)
def files():
    for path in (ROOT/"app").rglob("*"):
        if path.is_file() and not any(part in ("__pycache__",".pytest_cache") for part in path.parts):yield path
for name,paths in (("cytools-app.zip",list(files())),("CyTools_Subtitle-"+json.loads((ROOT/"app/CyTool.json").read_text("utf-8"))["version"]+"-source.zip",list(files())+[ROOT/"CyTools_Subtitle.exe",ROOT/"CyTools_Subtitle.sh",ROOT/"LISEZ-MOI.md",ROOT/"README.md",ROOT/"LICENSE",ROOT/".gitignore",ROOT/".gitleaks.toml"]+list((ROOT/"LICENCES").rglob("*")))):
    target=OUT/name
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            if not path.is_file():continue
            relative=path.relative_to(ROOT).as_posix()
            info=zipfile.ZipInfo.from_file(path,relative)
            if path.suffix==".sh":info.external_attr=(stat.S_IFREG|0o755)<<16
            archive.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(target.suffix+".sha256").write_text(digest+"  "+name+"\n","ascii")
    print(json.dumps({"file":str(target),"sha256":digest,"bytes":target.stat().st_size}))

"""Verify or reproduce the selected, unmodified CyUI Python snapshot.

Usage: python app/sync_cyui.py --check
       python app/sync_cyui.py --sync --source /path/to/CyUI
No network fetch, package install or upstream checkout modification occurs.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

APP=Path(__file__).resolve().parent


def verify():
    pin=json.loads((APP/'cyui-source.json').read_text('utf-8'))
    for relative,expected in pin['files'].items():
        path=APP/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('CyUI snapshot mismatch: '+relative)
        for node in ast.walk(ast.parse(path.read_text('utf-8'))):
            if isinstance(node,ast.ImportFrom):
                module=node.module or ''
                dependency=None
                if node.level==1:dependency='cyui_modules/'+module.replace('.','/')+'.py'
                elif module.startswith('cyui_modules.'):dependency=module.replace('.','/')+'.py'
                if dependency and dependency not in pin['files']:raise ValueError('Missing selected dependency: '+dependency)
    actual={p.name for p in (APP/'cyui_modules').glob('*.py')}
    expected={Path(p).name for p in pin['files'] if p.startswith('cyui_modules/')}
    if actual!=expected:raise ValueError('Unexpected CyUI module files')
    return {'version':pin['version'],'revision':pin['revision'],'files':len(pin['files']),'modules':pin['modules'],'verified':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');parser.add_argument('--sync',action='store_true');parser.add_argument('--source',type=Path);args=parser.parse_args()
    pin=json.loads((APP/'cyui-source.json').read_text('utf-8'))
    if args.sync:
        if args.source is None:parser.error('--sync requires --source')
        # Read committed blobs so a dirty reference checkout cannot enter the product.
        blobs={name:subprocess.check_output(['git','show',pin['revision']+':python/'+name],cwd=args.source) for name in pin['files']}
        for name,data in blobs.items():
            if hashlib.sha256(data).hexdigest()!=pin['files'][name]:raise ValueError('Pinned upstream hash mismatch: '+name)
        for name,data in blobs.items():
            path=APP/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps(verify()))


if __name__=='__main__':main()

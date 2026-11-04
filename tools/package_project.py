#!/usr/bin/env python3
"""Package the entire PBIP project; exclude local caches and compiled tooling."""
import argparse
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.git','.pbi','__pycache__','.venv','node_modules','bin','obj'}


def package(output):
    output=Path(output).resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    files=[p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDE.intersection(p.relative_to(ROOT).parts) and p.resolve()!=output]
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):z.write(p,'LaborMarket-PowerBI/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Invalid archive entry: '+bad)
        if not any(n.endswith('/Open-Project.ps1') for n in z.namelist()):raise RuntimeError('Missing launch helper')
    print(f'{output}: {len(files)} files, {output.stat().st_size:,} bytes; archive CRC verified.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    package(parser.parse_args().output)

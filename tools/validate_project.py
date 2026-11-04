#!/usr/bin/env python3
"""Offline PBIR schema and cross-reference checks. Requires jsonschema>=4.18."""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://developer.microsoft.com/json-schemas/'


def check(condition, message):
    if not condition: raise AssertionError(message)


def validate():
    store = {}
    for path in (ROOT/'tools'/'schemas').rglob('*.json'):
        obj = json.loads(path.read_text(encoding='utf-8'))
        store[BASE + path.relative_to(ROOT/'tools'/'schemas').as_posix()] = obj
        if '$id' in obj: store[obj['$id']] = obj
    registry = Registry().with_resources((url,Resource.from_contents(schema)) for url,schema in store.items())
    documents = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or 'schemas' in path.parts or 'source' in path.parts: continue
        if path.suffix not in {'.json','.pbip','.pbir','.pbism'}: continue
        obj = json.loads(path.read_text(encoding='utf-8'))
        if '$schema' not in obj:continue
        check(obj['$schema'] in store,f'No offline schema for {path}')
        validator=jsonschema.Draft7Validator(store[obj['$schema']],registry=registry)
        validator.validate(obj)
        documents.append((path,obj))
    manifest = json.loads((ROOT/'docs'/'project-manifest.json').read_text())
    tables = manifest['tables']
    measures = set(manifest['measures'])
    project_path = next(ROOT.glob('*.pbip'))
    project = json.loads(project_path.read_text())
    report_path = ROOT/project['artifacts'][0]['report']['path']
    ref = json.loads((report_path/'definition.pbir').read_text())['datasetReference']['byPath']['path']
    check((report_path/ref/'definition.pbism').exists(),'Missing semantic model')
    pages_meta = json.loads((report_path/'definition/pages/pages.json').read_text())
    pages = {p.parent.name:json.loads(p.read_text()) for p in (report_path/'definition/pages').glob('*/page.json')}
    check(set(pages_meta['pageOrder'])==set(pages),'Page order does not match real pages')
    bookmarks = {p.name.removesuffix('.bookmark.json'):json.loads(p.read_text()) for p in (report_path/'definition/bookmarks').glob('*.bookmark.json')}
    counts = {'schema_documents':len(documents),'pages':len(pages),'visuals':0,'field_references':0,'actions':0,'bookmarks':len(bookmarks)}

    def fields(value):
        if isinstance(value,dict):
            for typ in ['Column','Measure']:
                if typ not in value:continue
                expr=value[typ]
                source=expr.get('Expression',{}).get('SourceRef',{})
                if 'Entity' not in source:continue  # Internal aliases are checked by the JSON schema.
                t=source['Entity'];p=expr['Property']
                check(t in tables,f'Unknown entity: {t}')
                check(p in (measures if typ=='Measure' else tables[t]['columns']),f'Unknown {typ}: {t}.{p}')
                counts['field_references']+=1
            for v in value.values():fields(v)
        elif isinstance(value,list):
            for v in value: fields(v)

    for pid,page in pages.items():
        vs={p.parent.name:json.loads(p.read_text()) for p in (report_path/'definition/pages'/pid/'visuals').glob('*/visual.json')}
        counts['visuals']+=len(vs)
        for name,v in vs.items():
            check(v['name']==name,'Visual directory/name mismatch')
            pos=v['position']
            check(0<=pos['x'] and 0<=pos['y'] and pos['x']+pos['width']<=page['width'] and pos['y']+pos['height']<=page['height'],f'Visual outside canvas: {pid}/{name}')
            fields(v)
            for action in v['visual'].get('objects',{}).get('action',[]):
                props=action['properties'];kind=props['type']['expr']['Literal']['Value'].strip("'")
                target=props['destination' if kind=='PageNavigation' else 'bookmark']['expr']['Literal']['Value'].strip("'")
                check(target in (pages if kind=='PageNavigation' else bookmarks),f'Dead button: {target}')
                counts['actions']+=1
        for interaction in page.get('visualInteractions',[]):
            check(interaction['source'] in vs and interaction['target'] in vs,'Interaction references missing visual')
        if pid==manifest['homePage']:
            for gid,panel in manifest['panels'].items():
                for source in [panel['dateSlicer'],panel['periodSlicer']]:
                    actual={i['target'] for i in page['visualInteractions'] if i['source']==source and i['type']=='DataFilter'}
                    check(actual==set(panel['chart']),f'Slicer leaks into other panels: {gid}')
    for bookmark in bookmarks.values():
        for pid,section in bookmark['explorationState']['sections'].items():
            check(pid in pages,'Bookmark references missing page')
            for target in bookmark['options']['targetVisualNames']:
                check((report_path/'definition/pages'/pid/'visuals'/target/'visual.json').exists(),'Bookmark references missing visual')
    graphs=list(csv.DictReader((ROOT/'data/GraphTbl.csv').open(encoding='utf-8-sig')))
    mappings=list(csv.DictReader((ROOT/'data/SeriesGraphTbl.csv').open(encoding='utf-8-sig')))
    graph_ids={g['graph_id'] for g in graphs}
    check(all(m['graph_id'] in graph_ids for m in mappings),'Orphan series mappings')
    check(len({m['mapping_id'] for m in mappings})==len(mappings),'Duplicate series mappings')
    check(all('<X>' not in m['series_code_id'] and ',' not in m['series_code_id'] for m in mappings),'Unexpanded series definitions')
    check({m['transform'] for m in mappings if m['graph_id']=='g04'}=={'Raw','MA4Q'},'Lost raw/moving-average wage series')
    print(json.dumps(counts,indent=2))
    return counts


if __name__=='__main__':
    try:validate()
    except (AssertionError,jsonschema.ValidationError) as e:
        print(str(e),file=sys.stderr)
        raise SystemExit(1)

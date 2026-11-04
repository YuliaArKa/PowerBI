#!/usr/bin/env python3
"""Render a clearly labelled HTML layout guide from the PBIR home-page files.

This does not render Power BI. No series observations or simulated chart paths
are drawn. The guide exists to review positioning, Hebrew text and colour tokens.
"""
import csv
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def val(value,default=None):
    if not isinstance(value,dict):return default
    if 'solid' in value:return val(value['solid']['color'],default)
    try:
        v=value['expr']['Literal']['Value']
        if v in {'true','false'}:return v=='true'
        if v.startswith("'"):return v[1:-1].replace("''", "'")
        return float(v.rstrip('D'))
    except (KeyError,ValueError,AttributeError):return default


def props(v,key):
    entries=v.get(key,[])
    return entries[0].get('properties',{}) if entries else {}


def generate():
    manifest=json.loads((ROOT/'docs/project-manifest.json').read_text())
    pid=manifest['homePage']
    report=next(ROOT.glob('*.Report'))
    path=report/'definition/pages'/pid/'visuals'
    visuals=[json.loads(p.read_text()) for p in path.glob('*/visual.json')]
    visuals.sort(key=lambda x:x['position']['z'])
    maps=list(csv.DictReader((ROOT/'data/SeriesGraphTbl.csv').open(encoding='utf-8-sig')))
    fragments=[]
    for v in visuals:
        p=v['position'];visual=v['visual'];typ=visual['visualType'];o=visual.get('objects',{})
        bg=props(visual.get('visualContainerObjects',{}),'background')
        style=f"left:{p['x']}px;top:{p['y']}px;width:{p['width']}px;height:{p['height']}px;"
        if val(bg.get('show')):style+='background:'+val(bg.get('color'),'white')+';'
        content=''
        if typ=='textbox':
            for para in props(o,'general').get('paragraphs',[]):
                runs=''
                for r in para['textRuns']:
                    ts=r.get('textStyle',{})
                    runs+='<span style="font-size:'+ts.get('fontSize','12pt')+';font-weight:'+ts.get('fontWeight','normal')+';color:'+ts.get('color','#193B60')+'">'+html.escape(r['value'])+'</span>'
                content+='<div style="padding:2px 4px;text-align:'+para.get('horizontalTextAlignment','right')+'" dir="auto">'+runs+'</div>'
        elif typ=='actionButton':
            text=props(o,'text');label=val(text.get('text'),'')
            ink=val(text.get('fontColor'),'#193B60')
            content=f'<div class="button" style="font-size:12pt;color:{ink}">{html.escape(label)}</div>'
        elif typ=='card':
            field=visual['query']['queryState']['Values']['projections'][0]['field']['Measure']['Property']
            label='יש להוסיף נתוני סדרות ולרענן את הדוח' if field=='Data Status' else '—'
            opts=props(o,'labels')
            content=f'<div class="card" style="color:{val(opts.get("color"),"#193B60")};font-size:{val(opts.get("fontSize"),14)}pt">{html.escape(label)}</div>'
        elif typ=='tableEx':
            filt=v['filterConfig']['filters'][0]['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value'].strip("'")
            rows=sorted([m for m in maps if m['graph_id']==filt],key=lambda x:int(x['series_order']))
            content='<table class="kpi">'+''.join('<tr><td class="arrow"></td><td>—</td><td>—</td><td dir="rtl">'+html.escape(m['row_label'])+'</td></tr>' for m in rows)+'</table>'
        elif typ in {'lineChart','lineClusteredColumnComboChart'}:
            w=int(p['width']);h=int(p['height'])
            svg=f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-label="No observations">'
            for y in range(28,h-55,42):svg+=f'<line x1="45" x2="{w-42}" y1="{y}" y2="{y}" stroke="#E5E8EC" stroke-dasharray="2 4" />'
            svg+=f'<text x="{w/2}" y="{h/2}" text-anchor="middle" fill="#728197" font-size="16">אין נתוני תצפיות</text>'
            labels=[]
            for role in ['Y','Y2']:
                for proj in visual['query']['queryState'].get(role,{}).get('projections',[]):labels.append(proj.get('displayName',proj['nativeQueryRef']))
            legend=' · '.join(labels)
            svg+=f'<text x="{w/2}" y="{h-16}" text-anchor="middle" fill="#728197" font-size="12">{html.escape(legend)}</text></svg>'
            content=svg
        elif typ=='slicer':
            field=visual['query']['queryState']['Values']['projections'][0]['field']['Column']['Property']
            if field=='Date':
                content='<div class="range-labels"><span>01/01/2011 ▦</span><span>31/12/2023 ▦</span></div><div class="range"><i></i><i></i></div>'
            else:content='<div class="periods"><span>1Y</span><span>5Y</span><span class="selected">All</span></div>'
        fragments.append('<div class="visual" style="'+style+'">'+content+'</div>')
    document='''<!doctype html><html lang="he"><meta charset="utf-8"><title>עמוד הבית — layout guide</title><style>
*{box-sizing:border-box}body{margin:0;background:#e8ebef;font-family:Arial,sans-serif;color:#193B60}
.notice{width:650px;min-height:54px;background:#fff7dd;padding:10px 12px;line-height:1.4;font-size:12px;text-align:right}
.frame{width:650px;height:725px;overflow:hidden;background:white}
.canvas{width:1300px;height:1450px;position:relative;transform:scale(.5);transform-origin:top left;background:white}
.visual{position:absolute;overflow:hidden}.card,.button{height:100%;display:flex;align-items:center;justify-content:center;text-align:center}
.kpi{table-layout:fixed;width:100%;border-collapse:collapse;font-size:9pt}.kpi td{padding:8px 0;text-align:right;height:31px;white-space:nowrap}
.kpi td:nth-child(1){width:22px}.kpi td:nth-child(2){width:53px}.kpi td:nth-child(3){width:70px}.kpi td:nth-child(4){width:139px}
.range-labels{display:flex;justify-content:space-between;gap:5px;font-size:8px;padding:9px 4px 0}.range-labels span{background:white;border:1px solid #ddd;padding:3px}
.range{margin:18px 10px 0;height:2px;background:#555;display:flex;justify-content:space-between}.range i{height:24px;width:24px;background:white;border:1px solid #555;border-radius:50%;transform:translateY(-11px)}
.periods{display:flex;gap:5px;padding:2px;justify-content:center}.periods span{border:1px solid #888;background:#fff;border-radius:3px;padding:7px 12px;font-size:12pt}.periods .selected{background:#ddd}
</style><body><div class="notice" dir="rtl">תצוגת פריסה בלבד — לא סופקו נתוני סדרות. זו אינה תמונה מתוך Power BI Desktop, ואין כאן ערכי דוגמה.</div><div class="frame"><div class="canvas">'''+''.join(fragments)+'</div></div></body></html>'
    (ROOT/'docs/home-layout.html').write_text(document,encoding='utf-8')
    print('Wrote docs/home-layout.html; layout guide only, no observations.')


if __name__=='__main__':generate()
